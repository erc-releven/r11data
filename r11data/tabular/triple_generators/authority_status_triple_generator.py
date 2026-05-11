"""TripleGenerator for the Author groups sheet."""

import itertools
from collections.abc import Iterator
from functools import cached_property

from lodkit import _Triple, ttl
from r11data.tabular.models import AuthorityStatus, Place
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import aaao, crm, mkuri, r11spec, star
from rdflib import RDF, RDFS, Literal, URIRef


class AuthorityStatusRDFConverter(_ModelRDFConverter[AuthorityStatus]):
    @cached_property
    def person_uri(self) -> URIRef:
        person_model = self.get_person_data(self.model.authority_ascribed)
        return person_model.person_uri

    def base_triples(self) -> Iterator[_Triple]:
        e13_aaao_zp96_uri = mkuri()

        yield from ttl(
            e13_aaao_zp96_uri,
            (RDF.type, star.E13_aaao_ZP96),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.model.status_uri,
                    (RDF.type, aaao.ZE50_Authority_Status),
                    (RDFS.label, self.model.authority_status_label),
                ),
            ),
            (crm.P141_assigned, self.person_uri),
        )

        yield from self.authority_passage_triples(e13_aaao_zp96_uri)

    def e17_type_assertion_triples(self) -> Iterator[_Triple]:
        if (status_type := self.model.authority_status_type) is None:
            return

        authority_type_uri: URIRef = mkuri("Authority status type", status_type)

        yield from ttl(
            mkuri(),
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P14_carried_out_by, self.sheets.owner_id),
            (crm.P41_classified, self.model.status_uri),
            (
                crm.P42_assigned,
                ttl(
                    authority_type_uri,
                    (RDF.type, r11spec.Authority_Status_Type),
                    (RDFS.label, status_type),
                ),
            ),
        )

    def status_ascribing_authority_assertion_triples(self) -> Iterator[_Triple]:
        if (authority := self.model.authority_ascribed_by) is None:
            return

        authority_model = self.get_person_data(authority)

        e13_aaao_zp42_uri, e13_crm_p14_uri, ze13_speech_act_uri = (
            mkuri(),
            mkuri(),
            mkuri(),
        )

        yield from ttl(
            e13_aaao_zp42_uri,
            (RDF.type, star.E13_aaao_ZP42),
            (
                crm.P140_assigned_attribute_to,
                ttl(ze13_speech_act_uri, (RDF.type, aaao.ZE13_Speech_Act)),
            ),
            (crm.P141_assigned, self.model.status_uri),
        )

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, ze13_speech_act_uri),
            (crm.P141_assigned, authority_model.person_uri),
        )

        # p14/p17/p67 triples
        yield from self.authority_passage_triples(e13_aaao_zp42_uri)
        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def geographic_scope_assertion_triples(self) -> Iterator[_Triple]:
        if (geopgrahic_scope := self.model.geographic_scope) is None:
            return

        e13_aaao_zp114_uri = mkuri()
        site_model: Place = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=geopgrahic_scope,
            strict=True,
        )

        yield from ttl(
            e13_aaao_zp114_uri,
            (RDF.type, star.E13_aaao_ZP114),
            (crm.P140_assigned_attribute_to, self.model.status_uri),
            (crm.P141_assigned, ttl(site_model.place_uri, (RDF.type, crm.E27_Site))),
        )

        yield from self.authority_passage_triples(e13_aaao_zp114_uri)

    def temporal_scope_assertion_triples(self) -> Iterator[_Triple]:
        temporal_start, temporal_end = (
            self.model.temporal_start,
            self.model.temporal_end,
        )

        if not (temporal_start or temporal_end):
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.status_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        if temporal_start:
            yield from generate_date_triples(e52_uri, temporal_start)

        if temporal_end:
            yield from generate_date_triples(e52_uri, temporal_end)

    def __iter__(self) -> Iterator:
        return itertools.chain(
            self.base_triples(),
            self.e17_type_assertion_triples(),
            self.status_ascribing_authority_assertion_triples(),
            self.geographic_scope_assertion_triples(),
            self.temporal_scope_assertion_triples(),
        )
