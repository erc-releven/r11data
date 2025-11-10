"""TripleGenerator for the Author groups sheet."""

from collections.abc import Iterator
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import ActorGroup
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, pwro, star
from rdflib import RDF, RDFS, URIRef


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

        if (text_publication := self.model.source_text_publication) is not None:
            passage_uri = mkuri(
                f"{text_publication} - {self.model.source_text_reference}"
            )
            yield (passage_uri, crm.P67_refers_to, e13_pwro_wp5_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_pwro_wp5_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(self.base_triples())
