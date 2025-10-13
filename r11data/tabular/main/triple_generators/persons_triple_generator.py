"""TripleGenerator for the Persons sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from lodkit import _Triple, ttl
import pandas as pd
from r11data.tabular.main.models import Person
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import (
    crm,
    get_source_name_lang_tag,
    lrm,
    mkuri,
    r11,
    r11pros,
    r11spec,
    star,
)
from rdflib import Literal, RDF, RDFS, URIRef
import structlog


logger = structlog.get_logger()


class PersonRDFConverter(_ModelRDFConverter[Person]):
    @cached_property
    def person_uri(self):
        person_uri = (
            mkuri(self.model.identifier)
            if (_wisski_id := self.model.wisski_id) is None
            else URIRef(_wisski_id)
        )
        return person_uri

    def base_triples(self) -> Iterator[_Triple]:
        yield (self.person_uri, RDF.type, crm.E21_Person)

        if (name := self.model.descriptive_name) is not None:
            yield (self.person_uri, RDFS.label, Literal(name))

    def identifier_triples(self) -> Iterator[_Triple]:
        service_uri = URIRef(self.model.service)

        yield (service_uri, RDF.type, lrm.F11_Corporate_Body)
        yield from ttl(
            mkuri(),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P14_carried_out_by, service_uri),
            (crm.P140_assigned_attribute_to, self.person_uri),
            (
                crm.P37_assigned,
                [
                    (RDF.type, crm.E42_Identifier),
                    (crm.P190_has_symbolic_content, self.model.identifier),
                ],
            ),
        )

    def passage_triples(self) -> Iterator[_Triple]:
        if (reference := self.model.source_text_reference) is None:
            return

        passage_uri = mkuri(f"{self.model.source_text_publication} - {reference}")

        yield from ttl(
            passage_uri, (RDF.type, crm.E33_Linguistic_Object), (RDFS.label, reference)
        )

        if (excerpt := self.model.source_text_excerpt) is not None:
            yield (
                passage_uri,
                crm.P190_has_symbolic_content,
                Literal(excerpt),
            )

    def publication_triples(self) -> Iterator[_Triple]:
        if (publication := self.model.source_text_publication) is None:
            return
        publication_uri = mkuri(f"{publication}")

        yield from ttl(
            publication_uri,
            (RDF.type, r11.Publication),
            (RDFS.label, self.publication_label),
        )

    def complex_work_triples(self) -> Iterator[_Triple]:
        publication = self.model.source_text_publication
        reference = self.model.source_text_reference

        if publication is None and reference is None:
            return

        passage_uri = mkuri(f"{publication} - {reference}")
        publication_uri = mkuri(f"{publication}")
        e13_lrmoo_r15_uri = mkuri()

        yield from ttl(
            e13_lrmoo_r15_uri,
            (RDF.type, star.E13_lrmoo_R15),
            (crm.P140_assigned_attribute_to, passage_uri),
            (crm.P141_assigned, publication_uri),
            (crm.P14_carried_out_by, self.sheets.owner_id),
        )

        yield (publication_uri, crm.P67_refers_to, e13_lrmoo_r15_uri)

    def appellation_assertion_triples(self):
        e13_crm_p1_uri = mkuri()
        e33_e41_uri = mkuri()

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )

        # base appellation triples
        yield from ttl(
            e13_crm_p1_uri,
            (RDF.type, star.E13_crm_P1),
            (crm.P140_assigned_attribute_to, self.person_uri),
            (crm.P141_assigned, e33_e41_uri),
        )

        yield (passage_uri, crm.P67_refers_to, e13_crm_p1_uri)

        # name triples
        if (name_orig := self.model.name_in_sources_orig) is not None:
            lang = get_source_name_lang_tag(name_orig)
            yield (e33_e41_uri, crm.P141_assigned, Literal(name_orig, lang=lang))

        if (name_transl := self.model.name_in_sources_transl) is not None:
            yield (e33_e41_uri, crm.P141_assigned, Literal(name_transl, lang="en"))

        # authority triples + relational lookup
        if (authority_data := self.authority_data) is None:
            return

        person_uri, person_label = authority_data

        yield from ttl(
            person_uri, (RDF.type, crm.E21_Person), (RDFS.label, person_label)
        )
        yield (e13_crm_p1_uri, crm.P14_carried_out_by, person_uri)

    def gender_appellation_triples(self) -> Iterator[_Triple]:
        if self.model.gender_assignment is None:
            return

        e13_crm_p41_uri = mkuri()
        gender_assignment_uri = mkuri(f"{self.model.identifier} - gender")

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )

        yield (gender_assignment_uri, RDF.type, r11spec.Gender_Assignment)

        yield from ttl(
            e13_crm_p41_uri,
            (RDF.type, star.E13_crm_P41),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (crm.P141_assigned, self.person_uri),
        )

        yield (passage_uri, crm.P67_refers_to, e13_crm_p41_uri)

        if (authority_data := self.authority_data) is not None:
            authority_uri, _ = authority_data
            yield (e13_crm_p41_uri, crm.P14_carried_out_by, authority_uri)

    def gender_identifier_triples(self) -> Iterator[_Triple]:
        if (gender := self.model.gender_assignment) is None:
            return

        e13_crm_p42_uri = mkuri()
        gender_assignment_uri = mkuri(f"{self.model.identifier} - gender")

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )

        yield from ttl(
            e13_crm_p42_uri,
            (RDF.type, star.E13_crm_P42),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (crm.P141_assigned, Literal(gender)),
        )

        yield (passage_uri, crm.P67_refers_to, e13_crm_p42_uri)

        if (authority_data := self.authority_data) is not None:
            authority_uri, _ = authority_data
            yield (e13_crm_p42_uri, crm.P14_carried_out_by, authority_uri)

    def ethnic_group_triples(self) -> Iterator[_Triple]:
        if (ethnicity := self.model.ethnicity) is None:
            return

        e13_crm_p107_uri = mkuri()
        ethnic_group_uri = mkuri(ethnicity)

        yield (ethnic_group_uri, RDF.value, Literal(ethnicity))

        yield from ttl(
            e13_crm_p107_uri,
            (RDF.type, star.E13_crm_P107),
            (crm.P140_assigned_attribute_to, ethnic_group_uri),
            (crm.P141_assigned, self.person_uri),
        )

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_crm_p107_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def social_role_triples(self) -> Iterator[_Triple]:
        if (social_role := self.model.social_role) is None:
            return

        # P13 triples
        e13_sdhss_p13_uri = mkuri()
        social_role_uri = mkuri()
        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )

        yield (social_role_uri, RDF.type, r11pros.C1)

        yield from ttl(
            e13_sdhss_p13_uri,
            (RDF.type, star.E13_sdhss_P13),
            (crm.P140_assigned_attribute_to, social_role_uri),
            (crm.P141_assigned, self.person_uri),
        )

        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p13_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p13_uri, crm.P14_carried_out_by, URIRef(authority_uri))

        # P14 triples
        e13_sdhss_p14_uri = mkuri()

        yield from ttl(
            e13_sdhss_p14_uri,
            (RDF.type, star.E13_sdhss_P14),
            (crm.P140_assigned_attribute_to, social_role_uri),
            (crm.P141_assigned, social_role),
        )

        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p14_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p14_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def legal_role_triples(self) -> Iterator[_Triple]:
        if (legal_role := self.model.legal_role) is None:
            return

        # P26 triples
        e13_sdhss_p26_uri = mkuri()
        legal_role_uri = mkuri()

        yield (legal_role_uri, RDF.type, r11pros.C13)

        yield from ttl(
            e13_sdhss_p26_uri,
            (RDF.type, star.E13_sdhss_P26),
            (crm.P140_assigned_attribute_to, legal_role_uri),
            (crm.P141_assigned, self.person_uri),
        )

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )
        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p26_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p26_uri, crm.P14_carried_out_by, URIRef(authority_uri))

        # P33 triples
        e13_sdhss_p33_uri = mkuri()

        yield from ttl(
            e13_sdhss_p33_uri,
            (crm.P140_assigned_attribute_to, legal_role_uri),
            (crm.P141_assigned, legal_role),
        )

        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p33_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p33_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def language_skill_triples(self) -> Iterator[_Triple]:
        if (language_skill := self.model.language_skill) is None:
            return

        # P38 triples
        e13_sdhss_p38_uri = mkuri()
        language_skill_uri = mkuri()

        yield (language_skill_uri, RDF.type, r11pros.C21)

        yield from ttl(
            e13_sdhss_p38_uri,
            (RDF.type, star.E13_sdhss_P38),
            (crm.P140_assigned_attribute_to, self.person_uri),
            (crm.P141_assigned, language_skill_uri),
        )

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )
        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p38_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p38_uri, crm.P14_carried_out_by, URIRef(authority_uri))

        # P37 triples
        e13_sdhss_p37_uri = mkuri()

        yield from ttl(
            e13_sdhss_p37_uri,
            (RDF.type, star.E13_sdhss_P37),
            (crm.P140_assigned_attribute_to, language_skill_uri),
            (crm.P141_assigned, language_skill),
        )

        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p37_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p37_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def religion_triples(self) -> Iterator[_Triple]:
        if (religion := self.model.religion) is None:
            return

        # P36 triples
        e13_sdhss_p36_uri = mkuri()
        religion_uri = mkuri()

        yield from ttl(
            e13_sdhss_p36_uri,
            (RDF.type, star.E13_sdhss_P36),
            (crm.P140_assigned_attribute_to, religion_uri),
            (crm.P141_assigned, self.person_uri),
        )

        passage_uri = mkuri(
            f"{self.model.source_text_publication} - {self.model.source_text_reference}"
        )
        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p36_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p36_uri, crm.P14_carried_out_by, URIRef(authority_uri))

        # P37 triples
        e13_sdhss_p35_uri = mkuri()

        yield from ttl(
            e13_sdhss_p35_uri,
            (RDF.type, star.E13_sdhss_P35),
            (crm.P140_assigned_attribute_to, religion_uri),
            (crm.P141_assigned, religion),
        )

        yield (passage_uri, crm.P67_refers_to, e13_sdhss_p35_uri)

        if (authory_data := self.authority_data) is not None:
            authority_uri, _ = authory_data
            yield (e13_sdhss_p35_uri, crm.P14_carried_out_by, URIRef(authority_uri))

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.identifier_triples(),
            self.passage_triples(),
            self.publication_triples(),
            self.complex_work_triples(),
            self.appellation_assertion_triples(),
            self.gender_appellation_triples(),
            self.gender_identifier_triples(),
            self.ethnic_group_triples(),
            self.social_role_triples(),
            self.legal_role_triples(),
            self.language_skill_triples(),
            self.religion_triples(),
        )
