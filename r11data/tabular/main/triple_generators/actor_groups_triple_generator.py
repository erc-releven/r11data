"""TripleGenerator for the Author groups sheet."""

from collections.abc import Iterator
import itertools

from rdflib import RDF, RDFS, URIRef

from lodkit import _Triple, ttl
from r11data.tabular.main.models import ActorGroup
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, pwro, star


class ActorGroupsRDFConverter(_ModelRDFConverter[ActorGroup]):
    def base_triples(self) -> Iterator[_Triple]:
        maniftest_group_uri = mkuri(self.model.group_identifier)

        yield from ttl(
            maniftest_group_uri,
            (RDF.type, pwro.WE4_Manifest_Group),
            (RDFS.label, self.model.group_identifier),
        )

        e13_pwro_wp5_uri = mkuri()

        yield from ttl(
            e13_pwro_wp5_uri,
            (RDF.type, star.E13_pwro_WP5),
            (crm.P140_assigned_attribute_to, maniftest_group_uri),
            (crm.P141_assigned, [(RDF.type, crm.E74_Group)]),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_pwro_wp5_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(self.base_triples())
