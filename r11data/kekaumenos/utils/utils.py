"""Kekaumenos extraction utils."""

from collections.abc import Iterator

import httpx
from lxml import etree as et


def httpx_run_sparql_query(
    endpoint: str, query: str, headers: dict | None = None
) -> httpx.Response:
    """Run a SPARQL query against an endpoint using httpx."""
    data = {"output": "json", "query": query}
    headers = (
        {
            "Accept": "application/sparql-results+json",
        }
        if headers is None
        else headers
    )

    response = httpx.post(
        endpoint,
        headers=headers,
        data=data,
    )

    return response


def get_bindings_from_dict(bindings_dict: dict) -> Iterator[dict]:
    """Generate flat result bindings from a response dict"""
    bindings = map(
        lambda binding: {k: v["value"] for k, v in binding.items()},
        bindings_dict["results"]["bindings"],
    )
    return bindings


def get_bindings_from_response(response: httpx.Response) -> Iterator[dict]:
    """Generate flat result bindings from a response object."""
    bindings_dict = response.json()
    return get_bindings_from_dict(bindings_dict)


def extract_text_from_xml(xml: str) -> str:
    """Extract and join text nodes from an XML string."""
    tree = et.fromstring(xml, et.HTMLParser())
    xpath_result: list[str] = tree.xpath("//text()")
    return "".join(xpath_result)


def strip_xml_nodes(iterator: Iterator[dict]) -> Iterator[dict]:
    """Strip XML from textContent nodes of response bindings."""
    text_content_key = "http://www.homermultitext.org/cts/rdf/hasTextContent"

    for d in iterator:
        if d.get("p", None) == text_content_key:
            xml = d["o"]
            d["o"] = extract_text_from_xml(xml)

        yield d


def group_iterator(iterator: Iterator[dict], *, by: str) -> dict:
    grouped = {}
    for binding in iterator:
        try:
            value = grouped[binding["object"]]
        except KeyError:
            grouped.update({binding["object"]: {}})
            value = grouped[binding["object"]]

        value.update({binding["p"]: binding["o"]})

    return grouped
