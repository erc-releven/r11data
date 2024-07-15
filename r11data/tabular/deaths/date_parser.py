"""Functionality for parsing and RDF-converting date entries."""

# postponed annotation eval (see pep563)
from __future__ import annotations
import calendar
from contextlib import suppress
import re
from typing import ClassVar, Optional

import convertdate
from pydantic import BaseModel, field_validator, model_validator
from r11data.tabular.deaths.utils.utils import byzantine_to_jd
from toolz.dicttoolz import valfilter


class InvalidDateException(Exception):
    """Exception for indicating invalid date entries.

    This exception is raised from the R11DateEntry model if a validator fails.
    """


def _get_raw_duration(date_entry: R11DateEntry) -> tuple[tuple, tuple]:
    """Get a tuple represenation from an R11DateEntry object."""
    _begin_values = (
        date_entry.year_begin,
        date_entry.month_begin,
        date_entry.day_begin,
    )
    _end_values = (date_entry.year_end, date_entry.month_end, date_entry.day_end)

    return _begin_values, _end_values


class R11DateEntry(BaseModel):
    """Model for r11 date entries."""

    # -- model fields --
    calendar: str
    year_begin: int
    year_end: Optional[int] = None
    month_begin: Optional[str] = None
    month_end: Optional[str] = None
    day_begin: Optional[int] = None
    day_end: Optional[int] = None
    known_limit: Optional[str] = None

    # -- class level attributes --
    _calendars: ClassVar[list[str]] = ["AM", "J", "A"]
    _month_index_mapping: ClassVar[dict[str, int]] = {
        name: index for index, name in enumerate(calendar.month_name[1:], start=1)
    }
    _known_limit_values: ClassVar[list[str]] = ["TPQ", "TAQ"]

    # -- validators --
    @field_validator("calendar")
    @classmethod
    def _calendar_validator(cls, value):
        """Validate calendar values.

        Checks if the received value for the 'calendar' slot is valid.
        """
        if value not in cls._calendars:
            raise InvalidDateException(
                f"Calendar value must be one of {cls._calendars}.\n"
                f"Received '{value}'."
            )
        return value

    @field_validator("year_end")
    @classmethod
    def _year_end_validator(cls, value, values):
        """Validate end year values.

        Checks if the received value for the 'year_end' slot is lt the begin year.
        """
        _year_begin_value = values.data["year_begin"]
        if value < _year_begin_value:
            raise InvalidDateException(
                f"Start year greater than end year ({_year_begin_value}-{value})."
            )
        return value

    @field_validator("month_begin", "month_end")
    @classmethod
    def _month_validator(cls, value):
        """Validate month values.

        Checks if the received value is a valid month name.
        """
        try:
            month_index = cls._month_index_mapping[value]
            return month_index
        except KeyError:
            raise InvalidDateException(
                f"Month values must be one of {list(cls._month_index_mapping)}.\n"
                f"Received '{value}'."
            )

    @field_validator("month_end")
    @classmethod
    def _month_end_validator(cls, value, values):
        """Validate month end values."""
        _month_begin_value = values.data["month_begin"]
        _year_begin_value = values.data["year_begin"]
        _year_end_value = values.data["year_end"]

        if (value < _month_begin_value) and _year_end_value is None:
            raise InvalidDateException(
                f"Start month greater than end month with only a single year specified "
                f"({_year_begin_value}, {_month_begin_value}-{value})."
            )
        return value

    @field_validator("day_begin", "day_end")
    @classmethod
    def _day_begin_validator(cls, value, values):
        """Validate begin day values.

        Note that this assumes that if day_begin is given,
        also year_begin and month_begin must be present.
        This adds additional checking since it does not make sense
        to have e.g. just a year and a day.
        """
        # https://stackoverflow.com/q/77250848/6455731
        with suppress(KeyError):
            _year_begin = values.data["year_begin"]
            _month_begin = values.data["month_begin"]

            # check for boundaries
            # note: general lt check for full dates is done in the model_validator
            if value > calendar._monthlen(_year_begin, _month_begin):
                raise InvalidDateException(
                    f"Day '{value}' out of bounds for "
                    f"year-month '{_year_begin}-{_month_begin}'."
                )

        return value

    @field_validator("known_limit")
    @classmethod
    def _known_limit_validator(cls, value):
        """Validate known limit values.

        Checks if the received value for the known limit slot is valid.
        """
        if value not in cls._known_limit_values:
            raise InvalidDateException(
                f"Known limit value must be one of {cls._known_limit_values}.\n"
                f"Received '{value}'."
            )
        return value

    @model_validator(mode="after")
    @classmethod
    def _complete_values(cls, data):
        """Model validator for R11DateEntry objects.

        The validator is used to assign values to slots
        and also to perform a final check on the start and end values.
        """
        # handle epagomenal days in armenian dates
        month_end_default = 13 if data.calendar == "A" else 12

        def day_end_default():
            """Calculate the month_end default value.

            Caveat: This depends on non-local data and should
            run only after data.month is finally determined.
            """
            if data.month_end == 13:
                day_end = 5
            elif data.calendar == "A":
                day_end = 30
            else:
                day_end = calendar._monthlen(data.year_end, data.month_end)
            return day_end

        # end values
        data.year_end = data.year_end or data.year_begin
        data.month_end = data.month_end or data.month_begin or month_end_default

        data.day_end = data.day_end or data.day_begin or day_end_default()

        # begin values
        data.month_begin = data.month_begin or 1
        data.day_begin = data.day_begin or 1

        # check if start date is lt end date
        _begin_values, _end_values = _get_raw_duration(data)

        if _begin_values > _end_values:
            raise InvalidDateException(
                "Begin values are greater than end values.\n"
                f"Begin values: {_begin_values}, end values: {_end_values}."
            )


class R11DateParser:
    """Parse R11 table date entries.

    The input data (a raw R11 date string) is processed using a regex;
    capture groups are used to instantiate an R11DateEntry dataclass.
    """

    _jd_converters = {
        "AM": byzantine_to_jd,
        "A": convertdate.armenian.to_jd,
        "J": convertdate.julianday.from_julian,
    }

    def __init__(self, date_value: str):
        """Initialize a R11DateParser.

        Constructs a R11DateEntry component from a raw date_value string.
        """
        self._date_value = date_value
        self._date_entry_kwargs = valfilter(
            lambda x: x is not None, self._parse_date(self._date_value)
        )
        # use dependency injection?
        self.date_entry = R11DateEntry(**self._date_entry_kwargs)

    @staticmethod
    def _split_date_part(
        date_part: str, pattern: str = r"(\w+)?(?:/|-(\w+))?"
    ) -> tuple[str | None, str | None]:
        """Split a partial date entry by pattern.

        Helper for parse_date function.
        """
        _match_groups = re.match(pattern, date_part).groups()
        x, y, *_ = *_match_groups, None
        return (x, y)

    def _parse_date(self, date_entry: str) -> dict[str, str | None]:
        """Parse a date string and generate a mapping."""
        # R11DateEntry.model_fields.keys()
        keys = (
            "calendar",
            "year_begin",
            "year_end",
            "month_begin",
            "month_end",
            "day_begin",
            "day_end",
            "known_limit",
        )

        _date_split = date_entry.split(" ")
        _date_parts = (*_date_split, *[""] * (len(keys) - len(_date_split)))

        calendar = _date_parts[0]
        year_begin, year_end = self._split_date_part(_date_parts[1])
        month_begin, month_end = self._split_date_part(_date_parts[2])
        day_begin, day_end = self._split_date_part(_date_parts[3])

        _known_limit_match = re.search(r"\[(\w+)\]$", date_entry)
        known_limit = _known_limit_match.groups()[0] if _known_limit_match else None

        values = (
            calendar,
            year_begin,
            year_end,
            month_begin,
            month_end,
            day_begin,
            day_end,
            known_limit,
        )

        return dict(zip(keys, values))

    @property
    def raw_duration(self) -> tuple[tuple, tuple]:
        """Duration represented as iso8601 tuples."""
        return _get_raw_duration(self.date_entry)

    @property
    def jd_duration(self) -> tuple[int, int]:
        """Duration represented as tuple Julian days."""
        _begin_values, _end_values = self.raw_duration
        _converter = self._jd_converters[self.date_entry.calendar]

        return int(_converter(*_begin_values)), int(_converter(*_end_values))
