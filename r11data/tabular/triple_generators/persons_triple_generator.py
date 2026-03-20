"""TripleGenerator for the Persons sheet."""

from collections.abc import Iterator
from functools import cached_property, partial
import itertools
from typing import cast

from lodkit import _Triple, ttl
from r11data.tabular.models import Person
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
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
    def base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.model.person_uri,
            (RDF.type, crm.E21_Person),
            (RDFS.label, Literal(self.model.descriptive_name)),
        )

    def identifier_triples(self) -> Iterator[_Triple]:
        service_uri = URIRef(self.model.service)
        yield (service_uri, RDF.type, lrm.F11_Corporate_Body)

        yield from ttl(
            mkuri(crm.E15_Identifier_Assignment, self.model.identifier, service_uri),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P14_carried_out_by, service_uri),
            (crm.P140_assigned_attribute_to, self.model.person_uri),
            (
                crm.P37_assigned,
                ttl(
                    mkuri(crm.E42_Identifier, self.model.identifier, service_uri),
                    (RDF.type, crm.E42_Identifier),
                    (crm.P190_has_symbolic_content, self.model.identifier),
                    (RDFS.label, self.model.identifier),
                ),
            ),
        )

    def passage_triples(self) -> Iterator[_Triple]:
        if (publication_uri := self.model.publication_uri) is None:
            return

        yield from ttl(
            publication_uri,
            (RDF.type, r11.Publication),
            (RDFS.label, self.publication_label),
        )

        # passage assertions
        passage_uri = self.model.passage_uri
        assert isinstance(passage_uri, URIRef)

        yield from ttl(
            passage_uri,
            (RDF.type, crm.E33_Linguistic_Object),
            (RDFS.label, self.model.source_text_reference),
        )
        if (excerpt := self.model.source_text_excerpt) is not None:
            yield (passage_uri, crm.P190_has_symbolic_content, Literal(excerpt))

        # R15 assertions
        e13_lrmoo_r15_uri = mkuri()
        yield from ttl(
            e13_lrmoo_r15_uri,
            (RDF.type, star.E13_lrmoo_R15),
            (crm.P140_assigned_attribute_to, publication_uri),
            (crm.P141_assigned, passage_uri),
        )

        yield from self.authority_passage_triples(
            e13_uri=e13_lrmoo_r15_uri, authority_uri=self.sheets.owner_id
        )

    def appellation_assertion_triples(self) -> Iterator[_Triple]:
        e13_crm_p1_uri = mkuri()
        e33_e41_uri = mkuri()

        yield from ttl(
            e13_crm_p1_uri,
            (RDF.type, star.E13_crm_P1),
            (crm.P140_assigned_attribute_to, self.model.person_uri),
            (crm.P141_assigned, e33_e41_uri),
        )

        if (name_orig := self.model.name_in_sources_orig) is not None:
            lang = get_source_name_lang_tag(name_orig)
            yield (
                e33_e41_uri,
                crm.P190_has_symbolic_content,
                Literal(name_orig, lang=lang),
            )

        if (name_transl := self.model.name_in_sources_transl) is not None:
            yield (
                e33_e41_uri,
                crm.P190_has_symbolic_content,
                Literal(name_transl, lang="en"),
            )

        yield from self.authority_passage_triples(e13_crm_p1_uri)

    def gender_appellation_triples(self) -> Iterator[_Triple]:
        if self.model.gender_assignment is None:
            return

        e13_crm_p41_uri = mkuri()
        gender_assignment_uri = mkuri(
            self.model.id_string, "gender"
        )  # hashing for internal connection

        yield from ttl(
            e13_crm_p41_uri,
            (RDF.type, star.E13_crm_P41),
            (
                crm.P140_assigned_attribute_to,
                ttl(gender_assignment_uri, (RDF.type, r11spec.Gender_Assignment)),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p41_uri)

    def gender_identifier_triples(self) -> Iterator[_Triple]:
        if (gender := self.model.gender_assignment) is None:
            return

        e13_crm_p42_uri = mkuri()
        gender_assignment_uri = mkuri(self.model.id_string, "gender")

        yield from ttl(
            e13_crm_p42_uri,
            (RDF.type, star.E13_crm_P42),
            (crm.P140_assigned_attribute_to, gender_assignment_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri("Gender", gender),
                    (RDF.type, r11pros.C11),
                    (RDFS.label, gender),
                ),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p42_uri)

    def ethnic_group_triples(self) -> Iterator[_Triple]:
        if (ethnicity := self.model.ethnicity) is None:
            return

        e13_crm_p107_uri = mkuri()
        ethnic_group_uri = mkuri("Ethnicity", ethnicity)

        yield from ttl(
            e13_crm_p107_uri,
            (RDF.type, star.E13_crm_P107),
            (
                crm.P140_assigned_attribute_to,
                ttl(ethnic_group_uri, (RDF.value, ethnicity), (RDFS.label, ethnicity)),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p107_uri)

    def social_role_triples(self) -> Iterator[_Triple]:
        if (social_role := self.model.social_role) is None:
            return

        # P13 triples
        e13_sdhss_p13_uri = mkuri()
        social_role_uri = mkuri("Social role (C2)", social_role)

        yield from ttl(
            e13_sdhss_p13_uri,
            (RDF.type, star.E13_sdhss_P13),
            (
                crm.P140_assigned_attribute_to,
                ttl(social_role_uri, (RDF.type, r11pros.C1), (RDFS.label, social_role)),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # P14 triples
        e13_sdhss_p14_uri = mkuri()

        yield from ttl(
            e13_sdhss_p14_uri,
            (RDF.type, star.E13_sdhss_P14),
            (crm.P140_assigned_attribute_to, social_role_uri),
            (crm.P141_assigned, social_role),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_sdhss_p13_uri)
        yield from self.authority_passage_triples(e13_sdhss_p14_uri)

    def legal_role_triples(self) -> Iterator[_Triple]:
        if (legal_role := self.model.legal_role) is None:
            return

        # P26 triples
        e13_sdhss_p26_uri = mkuri()
        legal_role_uri = mkuri("Legal role (C12)", legal_role)

        yield from ttl(
            e13_sdhss_p26_uri,
            (RDF.type, star.E13_sdhss_P26),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    legal_role_uri,
                    (RDF.type, r11pros.C13),
                    (RDFS.label, legal_role),
                ),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # P33 triples
        e13_sdhss_p33_uri = mkuri()

        yield from ttl(
            e13_sdhss_p33_uri,
            (crm.P140_assigned_attribute_to, legal_role_uri),
            (crm.P141_assigned, legal_role),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_sdhss_p26_uri)
        yield from self.authority_passage_triples(e13_sdhss_p33_uri)

    def language_skill_triples(self) -> Iterator[_Triple]:
        if (language_skill := self.model.language_skill) is None:
            return

        # P38 triples
        e13_sdhss_p38_uri = mkuri()
        language_skill_uri = mkuri("Language", language_skill)

        yield from ttl(
            e13_sdhss_p38_uri,
            (RDF.type, star.E13_sdhss_P38),
            (crm.P140_assigned_attribute_to, self.model.person_uri),
            (
                crm.P141_assigned,
                ttl(
                    language_skill_uri,
                    (RDF.type, r11pros.C21),
                    (RDFS.label, language_skill),
                ),
            ),
        )

        # P37 triples
        e13_sdhss_p37_uri = mkuri()

        yield from ttl(
            e13_sdhss_p37_uri,
            (RDF.type, star.E13_sdhss_P37),
            (crm.P140_assigned_attribute_to, language_skill_uri),
            (crm.P141_assigned, language_skill),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_sdhss_p37_uri)
        yield from self.authority_passage_triples(e13_sdhss_p38_uri)

    def religion_triples(self) -> Iterator[_Triple]:
        if (religion := self.model.religion) is None:
            return

        # P36 triples
        e13_sdhss_p36_uri = mkuri()
        religion_uri = mkuri("Religious affiliation", religion)

        yield from ttl(
            e13_sdhss_p36_uri,
            (RDF.type, star.E13_sdhss_P36),
            (
                crm.P140_assigned_attribute_to,
                ttl(religion_uri, (RDF.type, r11pros.C23), (RDFS.label, religion)),
            ),
            (crm.P141_assigned, self.model.person_uri),
        )

        # P37 triples
        e13_sdhss_p35_uri = mkuri()

        yield from ttl(
            e13_sdhss_p35_uri,
            (RDF.type, star.E13_sdhss_P35),
            (crm.P140_assigned_attribute_to, religion_uri),
            (crm.P141_assigned, religion),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_sdhss_p35_uri)
        yield from self.authority_passage_triples(e13_sdhss_p36_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.identifier_triples(),
            self.passage_triples(),
            self.appellation_assertion_triples(),
            self.gender_appellation_triples(),
            self.gender_identifier_triples(),
            self.ethnic_group_triples(),
            self.social_role_triples(),
            self.legal_role_triples(),
            self.language_skill_triples(),
            self.religion_triples(),
        )
