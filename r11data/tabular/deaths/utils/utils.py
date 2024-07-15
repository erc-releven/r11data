"""General utilities for r11tab."""

from collections.abc import Callable, Container, Iterable, Mapping, Mapping
from contextlib import contextmanager
import functools
import json
from logging import Logger
import math
import operator
import os
import platform
import re
from typing import Any

from SPARQLWrapper import JSON, SPARQLWrapper
import convertdate
from dotenv import load_dotenv

from r11data.tabular.deaths.utils.loggers import logger
from rdflib import Graph, URIRef
from tabulardf import RowGraphConverter


load_dotenv()
PASSWD = os.environ["PASSWD"]


def get_uris_from_service(
    query_template: str,
    pbw_desc: str,
    name: str,
    code: str,
    source: str,
    endpoint: str | None = None,
) -> dict[str, URIRef] | None:
    """Get URIs from a remote endpoint.

    Constructs a SPARQL query and runs it against the WissKI service
    in order to obtain the URIs needed for triple generation in row_rule.
    """
    endpoint: str = (
        endpoint
        if endpoint is not None
        else "https://graphdb.r11.eu/repositories/RELEVEN"
    )

    deaths_query: str = query_template.format(
        pbw_desc=pbw_desc.replace('"', '\\"'), name=name, code=code
    )

    # sparqlwrapper setup + query
    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)
    sparql.setCredentials(user="admin", passwd=PASSWD)

    sparql.setQuery(deaths_query)

    sparql_result = sparql.queryAndConvert()

    # bind or skip + log
    result_bindings = sparql_result["results"]["bindings"]
    if not result_bindings:
        logger.warning(
            "The following SPARQL query returned empty:\n"
            f"{deaths_query}\n"
            f"Source: {source}\n"
        )
        return None

    result = {k: URIRef(v["value"]) for k, v in result_bindings[0].items()}

    return result


def byzantine_to_jd(year: int, month: int, day: int):
    """..."""
    byzantine_leap_days = math.floor(5509 / 4)
    byzantine_julian_days_delta = 5509 * 365 + byzantine_leap_days + 1

    julian_jd = convertdate.julian.to_jd(year=year, month=month, day=day)

    result_jd = operator.sub(julian_jd, byzantine_julian_days_delta)

    return result_jd


def getmap(d: Mapping, keys: Iterable["str"], default: Any = None):
    """Return the first key in keys that is found in a dictionary."""
    for key in keys:
        try:
            result = d[key]
            return result
        except KeyError:
            pass

    return default


def skipif(skip_callback: Callable = Graph, **kwargs: Container):
    """Decorator for checking kwargs of the decorated function against a container.

    If the containment check is False, skip_callback is invoked and its result returned.

    Example:

    @skipif(some_value=(1, 2, 3))
    def some_rule(row_data: Mapping):
        print("Doing stuff")

    some_rule({"some_value": 3})    # returns an empty graph
    some_rule({"some_value": 4})    # print
    """

    def _decor(f: Callable):
        @functools.wraps(f)
        def _wrapper(row_data: Mapping, **more_kwargs):
            for k, v in kwargs.items():
                value = row_data[k]
                if value in v:
                    logger.warning(
                        f"Skipping triple generator. Value of '{k}' binding is '{value}'."
                    )
                    return skip_callback()
            return f(row_data, **more_kwargs)

        return _wrapper

    return _decor


def remove_parens(s: str) -> str:
    """Remove parens and everything between those parens from a string."""
    return re.sub(r"\s\(.*[\)\}]", "", s)


@contextmanager
def log_context():
    logger.warning(f"Script started {'':+>79}")
    yield
    logger.warning(f"Script ended {'':->79}")


def get_system_information() -> str:
    info: dict = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }

    return json.dumps(info)
