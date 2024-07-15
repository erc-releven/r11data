"""Rule callables for TabulaRDF."""

from functools import partial
import itertools
from typing import Mapping
from uuid import uuid1

from rdflib import Graph, URIRef

from r11data.tabular.deaths.query_templates import (
    editor_deaths_template,
    source_deaths_template,
)
import r11data.tabular.deaths.triple_generators.deaths_editor_triple_generators as de
import r11data.tabular.deaths.triple_generators.deaths_source_triple_generators as ds
from r11data.tabular.deaths.triple_generators.metadata_triple_generator import (
    _generate_nodes_metadata,
)
from r11data.tabular.deaths.utils.namespaces import sd
from r11data.tabular.deaths.utils.utils import (
    get_uris_from_service,
    getmap,
    remove_parens,
    skipif,
)


SKIP_VALUES = {
    "Source": [
        "Council of 1157",
        "Italikos",
        "Niketas Choniates, Historia",
        "Pantokrator Typikon",
        "Prodromos, Historische Gedichte",
        "Tzetzes, Letters",
    ],
    "Name": ["Basileios"],
    "Source loc": ["2.178.5"],
}

skip = skipif(skip_callback=Graph, **SKIP_VALUES)

generate_nodes_metadata = _generate_nodes_metadata()


@skip
def source_row_rule(row_data: Mapping) -> Graph:
    """Callable responsible for generating a row graph in RowGraphConverter.

    See https://github.com/lu-pl/tabulardf#callable-converters.
    """
    # -- bindings --
    e13_subject_uri = sd[str(uuid1())]

    _date_value = row_data["Death date"]
    temporal_entity_uri = sd[str(uuid1())]

    pbw_desc = getmap(row_data, ("Description in PBW", "Description"))

    # query data bindings
    name, code, source = (
        remove_parens(row_data["Name"]),
        row_data["Code"],
        row_data["Source"],
    )

    query_result = get_uris_from_service(
        source_deaths_template, pbw_desc=pbw_desc, name=name, code=code, source=source
    )

    # -- graph generation --
    graph = Graph()

    # skip the entry if the query returns an empty set
    # this gets logged in get_uris_from_service
    if not query_result:
        return graph

    triples = itertools.chain(
        ds.generate_jd_trs_triples(),
        ds.generate_e13_triples(e13_subject_uri, temporal_entity_uri, **query_result),
        ds.generate_e2_triples(temporal_entity_uri, _date_value),
        generate_nodes_metadata(e13_subject_uri),
    )

    for triple in triples:
        graph.add(triple)

    return graph


@skip
def _editor_row_rule(row_data: Mapping, *, actor_p14) -> Graph:
    """Callable responsible for generating a row graph in RowGraphConverter."""
    # -- bindings --
    passage_uri = sd[str(uuid1())]
    e13_r15_uri = sd[str(uuid1())]
    e13_p4_uri = sd[str(uuid1())]
    temporal_entity_uri = sd[str(uuid1())]

    date_value = row_data["Death date"]
    pbw_desc = getmap(row_data, ("Description in PBW", "Description"))
    source = getmap(row_data, ("Source loc", "Outside source"))

    name, code, source = (
        remove_parens(row_data["Name"]),
        row_data["Code"],
        row_data["Source"],
    )

    query_result = get_uris_from_service(
        editor_deaths_template, pbw_desc=pbw_desc, name=name, code=code, source=source
    )

    # -- graph generation --
    graph = Graph()

    if not query_result:
        return graph

    triples = itertools.chain(
        de.generate_passage_triples(passage_uri, source),
        de.generate_e13_r15_triples(
            e13_r15_uri, query_result["pub"], passage_uri, actor_p14
        ),
        de.generate_e13_p4_triples(
            e13_p4_uri,
            query_result["d"],
            query_result["e"],
            temporal_entity_uri,
            passage_uri,
        ),
        ds.generate_e2_triples(temporal_entity_uri, date_value),
        generate_nodes_metadata(e13_p4_uri, e13_r15_uri),
    )

    for triple in triples:
        graph.add(triple)

    return graph


aa_uri = URIRef("https://r11.eu/rdf/resource/6527e16873d66")
mr_uri = URIRef("https://r11.eu/rdf/resource/6527e3ae5bb7c")

aa_editor_row_rule = partial(_editor_row_rule, actor_p14=aa_uri)
mr_editor_row_rule = partial(_editor_row_rule, actor_p14=mr_uri)
