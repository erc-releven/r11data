"""Triple generators for 'source' columns."""

from functools import partial
from typing import Callable, Iterator, Unpack

from lodkit import ttl
from lodkit.types import _Triple, _TripleObject
from pydantic import ValidationError
from r11data.tabular.deaths.date_parser import InvalidDateException, R11DateParser
from r11data.tabular.deaths.utils.loggers import logger
from r11data.tabular.deaths.utils.namespaces import crm, sd, star
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, TIME


def generate_e13_triples(
    e13_subject_uri: URIRef,
    temporal_entity_uri: URIRef,
    attrassign_uri: URIRef,
    death_uri: URIRef,
    authority_uri: URIRef,
    source_uri: URIRef,
) -> Iterator[_Triple]:
    """Generate E13 triples."""
    return ttl(
        e13_subject_uri,
        (RDF.type, star["E13_crm_P4"]),
        (crm["P140_assigned_attribute_to"], death_uri),
        (crm["P141_assigned"], temporal_entity_uri),
        (crm["P14_carried_out_by"], authority_uri),
        (crm["P17_was_motivated_by"], source_uri),
    )


def generate_jd_trs_triples() -> Iterator[_Triple]:
    """Generate static triples for Julian Day definition."""
    return ttl(
        sd["JulianDay"],
        (RDF.type, TIME.TRS),
        (RDF.type, RDFS.Datatype),
        (RDFS.isDefinedBy, URIRef("https://www.wikidata.org/entity/Q14267")),
    )


def _generate_time_base(
    temporal_entity_uri: URIRef,
    date_value: str,
    *args: Unpack[tuple[URIRef, _TripleObject]],
) -> Iterator[_Triple]:
    """..."""
    return ttl(
        temporal_entity_uri,
        (RDF.type, crm["E52_Time-Span"]),
        (RDFS.label, Literal(date_value)),
        *args,
    )


def _generate_time_triples(
    temporal_entity_uri: URIRef, date_parser: R11DateParser
) -> Iterator[_Triple]:
    """Logic for creating time triples based on an R11DateParser object.

    -- cases --
    1. position (begin == end):
    2. duration (begin != end)
    3 position/known_limit
      3.1 TAQ position
      3.2 TPQ position
    4 duration/known_limit
      4.1 TAQ duration
      4.2 TPQ duration
    """
    date_label = date_parser._date_value
    jd_begin, jd_end = date_parser.jd_duration
    is_position: bool = jd_begin == jd_end
    known_limit = date_parser.date_entry.known_limit

    jd = sd["JulianDay"]

    _time_base: Callable = partial(_generate_time_base, temporal_entity_uri, date_label)

    match is_position, known_limit:
        case True, None:
            time_triples = _time_base(
                (crm["P82_at_some_time_within"], Literal(jd_begin, datatype=jd))
            )
        case True, "TAQ":
            # end of the end
            time_triples = _time_base(
                (crm["P82b_end_of_the_end"], Literal(jd_begin, datatype=jd))
            )
        case True, "TPQ":
            # begin of the begin
            time_triples = _time_base(
                (crm["P82a_begin_of_the_begin"], Literal(jd_begin, datatype=jd))
            )
        case False, None:
            time_triples = _time_base(
                (crm["P82a_begin_of_the_begin"], Literal(jd_begin, datatype=jd)),
                (crm["P82b_end_of_the_end"], Literal(jd_end, datatype=jd)),
            )
        case False, "TAQ":
            # begin of the end, end of the end
            time_triples = _time_base(
                (crm["P81b_begin_of_the_end"], Literal(jd_begin, datatype=jd)),
                (crm["P82b_end_of_the_end"], Literal(jd_end, datatype=jd)),
            )
        case False, "TPQ":
            # begin of the begin, end of the begin
            time_triples = _time_base(
                (crm["P82a_begin_of_the_begin"], Literal(jd_begin, datatype=jd)),
                (crm["P81a_end_of_the_begin"], Literal(jd_end, datatype=jd)),
            )
        case _:
            raise Exception("Time triple switch failed.")

    return time_triples


def generate_e2_triples(
    temporal_entity_uri: URIRef, date_value: str
) -> Iterator[_Triple]:
    """Generate time_triples.

    Depending on the input data either
      - generate full time triples or
      - generate reduced time triples (given invalid input).
    """
    try:
        date_parser = R11DateParser(date_value)
        time_triples = _generate_time_triples(temporal_entity_uri, date_parser)

    except (InvalidDateException, ValidationError) as e:
        logger.warning(
            f"Could not create R11DateParser from value '{date_value}'.\n" f"{e}\n"
        )

        time_triples = _generate_time_base(temporal_entity_uri, date_value)

    return time_triples
