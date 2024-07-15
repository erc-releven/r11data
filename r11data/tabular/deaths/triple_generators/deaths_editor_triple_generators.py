"""Triple generators for 'editor' columns."""

from collections.abc import Iterator

from lodkit import ttl
from lodkit.types import _Triple
from r11data.tabular.deaths.utils.namespaces import crm, lrmoo
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD


def generate_passage_triples(passage: URIRef, outside_source: str) -> Iterator[_Triple]:
    """Generate passage triples."""
    return ttl(
        passage,
        (RDF.type, crm.E33_Linguistic_Object),
        (RDF.type, crm.E73_Information_Object),
        (crm.P3_has_note, Literal(outside_source, datatype=XSD.string)),
    )


def generate_e13_r15_triples(
    e13_r15_uri: URIRef, pub: URIRef, passage: URIRef, actor_p14: URIRef
) -> Iterator[_Triple]:
    """Generate E13_R15 triples."""
    return ttl(
        e13_r15_uri,
        (RDF.type, crm.E13_Attribute_Assignment),
        (crm.P140_assigned_attribute_to, pub),
        (crm.P177_assigned_property_of_type, lrmoo.R15_has_fragment),
        (crm.P141_assigned, passage),
        (crm.P14_carried_out_by, actor_p14),
    )


def generate_e13_p4_triples(
    e13_p4_uri: URIRef,
    death_uri: URIRef,
    person_uri: URIRef,
    temporal_entity_uri: URIRef,
    passage: URIRef,
):
    """Generate E13_P4 triples."""
    return ttl(
        e13_p4_uri,
        (RDF.type, crm.E13_Attribute_Assignment),
        (crm.P140_assigned_attribute_to, death_uri),
        (crm.P177_assigned_property_of_type, crm["P4_has_time-span"]),
        (crm.P141_assigned, temporal_entity_uri),
        (crm.P14_carried_out_by, person_uri),
        (crm.P17_was_motivated_by, passage),
    )
