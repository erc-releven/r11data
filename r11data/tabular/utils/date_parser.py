"""Functionality for parsing and RDF-converting date entries."""

import logging
import math
import operator
import re
from calendar import monthrange
from collections.abc import Iterator
from typing import Literal

import convertdate
from lodkit import _Triple
from pydantic import BaseModel, model_validator
from r11data.tabular.utils.rdf_utils import crm, r11spec
from rdflib import RDFS
from rdflib import Literal as RDFLiteral

logger = logging.getLogger(__name__)


Calendar = Literal["A", "AM", "J"]
Qualifier = Literal["TAQ", "TPQ"]

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


class DatePart(BaseModel):
    calendar: Calendar | None = None
    year: int
    month: int | None = None
    day: int | None = None
    qualifier: Qualifier | None = None


class DateRange(BaseModel):
    start: DatePart
    end: DatePart | None = None

    @model_validator(mode="after")
    def inherit_calendar(self) -> "DateRange":
        if self.end is not None and self.end.calendar is None:
            self.end.calendar = self.start.calendar
        return self


class ExpandedDateRange(BaseModel):
    calendar: Calendar | None = None

    start_year: int
    start_month: int
    start_day: int

    end_year: int
    end_month: int
    end_day: int

    start_qualifier: Qualifier | None = None
    end_qualifier: Qualifier | None = None


MONTH_RE = "|".join(MONTHS)

DATE_RE = re.compile(
    rf"""
    ^\s*
    (?:(?P<calendar>AM|A|J)\s*)?
    (?P<year>\d+)
    \s*[,;:]?\s*
    (?:
        (?P<month>{MONTH_RE})
        (?:\s+(?P<day>\d{{1,2}}))?
    )?
    \s*
    (?:
        \[?(?P<qualifier>TAQ|TPQ)\]?
    )?
    \s*$
    """,
    re.VERBOSE,
)


def parse_date_part(text: str) -> DatePart:
    match = DATE_RE.match(text)

    if not match:
        raise ValueError(f"Invalid date part: {text!r}")

    month_name = match.group("month")

    return DatePart(
        calendar=match.group("calendar"),
        year=int(match.group("year")),
        month=MONTHS[month_name] if month_name else None,
        day=int(match.group("day")) if match.group("day") else None,
        qualifier=match.group("qualifier"),
    )


def parse_date(text: str) -> DateRange:
    start_text, *rest = re.split(r"\s*-\s*", text, maxsplit=1)

    return DateRange(
        start=parse_date_part(start_text),
        end=parse_date_part(rest[0]) if rest else None,
    )


def lower_bound(part: DatePart) -> tuple[int, int, int]:
    return (
        part.year,
        part.month or 1,
        part.day or 1,
    )


def upper_bound(part: DatePart) -> tuple[int, int, int]:
    if part.month is None:
        match part.calendar:
            case "A":
                return part.year, 13, 5
            case "J" | "AM" | None:
                return part.year, 12, 31
            case _:
                raise AssertionError("unreachable")

    if part.day is None:
        match part.calendar:
            case "A":
                if 1 <= part.month <= 12:
                    return part.year, part.month, 30
                if part.month == 13:
                    return part.year, 13, 5
                raise ValueError(f"Invalid Armenian month: {part.month}")

            case "J" | "AM" | None:
                return part.year, part.month, monthrange(part.year, part.month)[1]

            case _:
                raise AssertionError("unreachable")

    return part.year, part.month, part.day


def expand_date_range(date_range: DateRange) -> ExpandedDateRange:
    start_part = date_range.start
    end_part = date_range.end or date_range.start

    start_year, start_month, start_day = lower_bound(start_part)
    end_year, end_month, end_day = upper_bound(end_part)

    return ExpandedDateRange(
        calendar=start_part.calendar,
        start_year=start_year,
        start_month=start_month,
        start_day=start_day,
        end_year=end_year,
        end_month=end_month,
        end_day=end_day,
        start_qualifier=start_part.qualifier,
        end_qualifier=end_part.qualifier,
    )


def parse_and_expand_date(text: str) -> ExpandedDateRange:
    return expand_date_range(parse_date(text))


##################################################
#### converters


def byzantine_to_jd(year: int, month: int, day: int):
    byzantine_leap_days = math.floor(5509 / 4)
    byzantine_julian_days_delta = 5509 * 365 + byzantine_leap_days + 1

    julian_jd = convertdate.julian.to_jd(year=year, month=month, day=day)
    result_jd = operator.sub(julian_jd, byzantine_julian_days_delta)

    return result_jd


jd_converters = {
    "AM": byzantine_to_jd,
    "A": convertdate.armenian.to_jd,
    "J": convertdate.julianday.from_julian,
}
##################################################


def _get_start_predicate(start_qualifier):
    match start_qualifier:
        case "TAQ":
            return crm.P81b_begin_of_the_end
        case "TPQ":
            return crm.P82a_begin_of_the_begin
        case None:
            return crm.P82a_begin_of_the_begin
        case _:
            assert False, "This should never happen."


def _get_end_predicate(end_qualifier):
    match end_qualifier:
        case "TAQ":
            return crm.P82b_end_of_the_end
        case "TPQ":
            return crm.P81a_end_of_the_begin
        case None:
            return crm.P82b_end_of_the_end
        case _:
            assert False, "This should never happen."


def generate_date_triples(e52_node, date: str) -> Iterator[_Triple]:
    try:
        date_range = parse_and_expand_date(date)

        converter = jd_converters[date_range.calendar]

        start_predicate = _get_start_predicate(date_range.start_qualifier)
        end_predicate = _get_end_predicate(date_range.end_qualifier)

        start_date = converter(
            date_range.start_year, date_range.start_month, date_range.start_day
        )
        end_date = converter(
            date_range.end_year, date_range.end_month, date_range.end_day
        )

    except Exception as exc:
        logger.warning(
            "Unable to compute date for %r: %s",
            date,
            exc,
        )
        return
    else:
        yield (e52_node, RDFS.label, RDFLiteral(date))
        yield (
            e52_node,
            start_predicate,
            RDFLiteral(start_date, datatype=r11spec.JulianDay),
        )
        yield (
            e52_node,
            end_predicate,
            RDFLiteral(end_date, datatype=r11spec.JulianDay),
        )
