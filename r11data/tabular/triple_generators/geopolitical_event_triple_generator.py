"""TripleGenerator for the Geopolitical Event sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import (
    ActorGroup,
    AuthorityStatus,
    GeopoliticalEvent,
    Person,
    Place,
)
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import (
    aaao,
    crm,
    get_source_name_lang_tag,
    lrm,
    mkuri,
    pwro,
    r11,
    r11pros,
    r11spec,
    star,
)
from rdflib import RDF, RDFS, Literal, URIRef


class GeopoliticalEventRDFConverter(_ModelRDFConverter[GeopoliticalEvent]):
    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.event_uri,
            (RDF.type, crm.E7_Activity),
            (RDFS.label, self.model.event_label),
        )

    def attack_event_assertion_triples(self) -> Iterator[_Triple]:
        e13_crm_p9_uri = mkuri()

        yield from ttl(
            e13_crm_p9_uri,
            (RDF.type, star.E13_crm_P9),
            (crm.P140_assigned_attribute_to, self.model.event_uri),
            (
                crm.P141_assigned,
                ttl(self.model.attack_event_uri, (RDF.type, pwro.WE6_Attack)),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p9_uri)

    def event_type_assertion_triples(self) -> Iterator[_Triple]:
        e17_uri = mkuri()

        yield from ttl(
            e17_uri,
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P14_carried_out_by, URIRef("https://r11.eu/")),
            (crm.P41_classified, self.model.event_uri),
            (
                crm.P42_assigned,
                ttl(
                    self.model.event_type_uri,
                    (RDF.type, r11spec.Geopolitical_Event_Type),
                    (RDFS.label, f"{self.model.event_type} (Event Type)"),
                ),
            ),
        )

    def active_party_assertion_triples(self) -> Iterator[_Triple]:
        if (involved_person := self.model.involved_person) is None:
            return

        involved_person_model: Person | None = self.get_person_data(
            involved_person, strict=False
        )

        if involved_person_model is None:
            return

        e13_crm_p14_uri = mkuri()

        yield from ttl(
            e13_crm_p14_uri,
            (RDF.type, star.E13_crm_P14),
            (crm.P140_assigned_attribute_to, self.model.event_uri),
            (crm.P141_assigned, involved_person_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p14_uri)

    def combatant_assertion_triples(self) -> Iterator[_Triple]:
        if (combatant := self.model.combatant) is None:
            return

        if (combatant_model := self.get_person_data(combatant, strict=False)) is None:
            return

        e13_pwro_wp16 = mkuri()

        yield from ttl(
            e13_pwro_wp16,
            (RDF.type, star.E13_pwro_WP16),
            (crm.P140_assigned_attribute_to, self.model.attack_event_uri),
            (crm.P141_assigned, combatant_model.person_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp16)

    def combatant_group_assertion_triples(self) -> Iterator[_Triple]:
        if (combatant_group := self.model.combatant_group) is None:
            return

        combatant_group_model: ActorGroup | None = self.lookup(
            sheet=self.sheets.actor_groups,
            model=ActorGroup,
            column="Group identifier",
            key=combatant_group,
            strict=False,
        )

        if combatant_group_model is None:
            return

        e13_pwro_wp16 = mkuri()

        yield from ttl(
            e13_pwro_wp16,
            (RDF.type, star.E13_pwro_WP16),
            (crm.P140_assigned_attribute_to, self.model.attack_event_uri),
            (crm.P141_assigned, combatant_group_model.group_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp16)

    def challenged_authority_assertion_triples(self) -> Iterator[_Triple]:
        if (challenge := self.model.challenge) is None:
            return

        challenge_model: AuthorityStatus | None = self.lookup(
            sheet=self.sheets.authority_status,
            model=AuthorityStatus,
            column="Authority status label",
            key=challenge,
            strict=False,
        )

        if challenge_model is None:
            return

        e13_aaao_zp100_uri = mkuri()

        yield from ttl(
            e13_aaao_zp100_uri,
            (RDF.type, star.E13_aaao_ZP100),
            (crm.P140_assigned_attribute_to, self.model.attack_event_uri),
            (crm.P141_assigned, challenge_model.status_uri),
        )

        yield from self.authority_passage_triples(e13_aaao_zp100_uri)

    def targeted_place_assertion_triples(self) -> Iterator[_Triple]:
        if (place := self.model.intended_target_place) is None:
            return

        place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=place,
            strict=False,
        )

        if place_model is None:
            return

        e13_pwro_wp6 = mkuri()

        yield from ttl(
            e13_pwro_wp6,
            (RDF.type, star.E13_pwro_WP6),
            (crm.P140_assigned_attribute_to, self.model.attack_event_uri),
            (crm.P141_assigned, place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_pwro_wp6)

    def targeted_population_assertion_triples(self) -> Iterator[_Triple]:
        if (population := self.model.intended_target_population) is None:
            return

        population_uri = mkuri("Population label", population)

        e13_pwro_wp6 = mkuri()

        yield from ttl(
            e13_pwro_wp6,
            (RDF.type, star.E13_pwro_WP6),
            (crm.P140_assigned_attribute_to, self.model.attack_event_uri),
            (crm.P141_assigned, ttl(population_uri, (RDF.type, aaao.ZE37_Population))),
        )

        yield from self.authority_passage_triples(e13_pwro_wp6)

    def event_created_place_assertion_triples(self) -> Iterator[_Triple]:
        if (created_place := self.model.created_place) is None:
            return

        created_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=created_place,
            strict=False,
        )

        if created_place_model is None:
            return

        place_production_event_uri = mkuri(
            crm.E12_Production, created_place_model.place_uri
        )

        e13_crm_p9_uri = mkuri()
        e13_crm_p108_uri = mkuri()

        yield from ttl(
            e13_crm_p9_uri,
            (RDF.type, star.E13_crm_p9),
            (crm.P140_assigned_attribute_to, self.model.event_uri),
            (
                crm.P141_assigned,
                ttl(
                    place_production_event_uri,
                    (RDF.type, crm.E12_Production),
                ),
            ),
        )

        yield from ttl(
            e13_crm_p108_uri,
            (RDF.type, star.E13_crm_P108),
            (crm.P140_assigned_attribute_to, place_production_event_uri),
            (crm.P141_assigned, created_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p9_uri)
        yield from self.authority_passage_triples(e13_crm_p108_uri)

    def event_destroyed_place_assertion_triples(self) -> Iterator[_Triple]:
        if (destroyed_place := self.model.created_place) is None:
            return

        destroyed_place_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=destroyed_place,
            strict=False,
        )

        if destroyed_place_model is None:
            return

        place_destruction_event_uri = mkuri(
            pwro.WE8_Intentional_Destruction, destroyed_place_model.place_uri
        )

        e13_crm_p9_uri = mkuri()
        e13_crm_p13_uri = mkuri()

        yield from ttl(
            e13_crm_p9_uri,
            (RDF.type, star.E13_crm_p9),
            (crm.P140_assigned_attribute_to, self.model.event_uri),
            (
                crm.P141_assigned,
                ttl(
                    place_destruction_event_uri,
                    (RDF.type, pwro.WE8_Intentional_Destruction),
                ),
            ),
        )

        yield from ttl(
            e13_crm_p13_uri,
            (RDF.type, star.E13_crm_P13),
            (crm.P140_assigned_attribute_to, place_destruction_event_uri),
            (crm.P141_assigned, destroyed_place_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p9_uri)
        yield from self.authority_passage_triples(e13_crm_p13_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.attack_event_assertion_triples(),
            self.event_type_assertion_triples(),
            self.active_party_assertion_triples(),
            self.combatant_assertion_triples(),
            self.combatant_group_assertion_triples(),
            self.challenged_authority_assertion_triples(),
            self.targeted_place_assertion_triples(),
            self.targeted_population_assertion_triples(),
            self.event_created_place_assertion_triples(),
            self.event_destroyed_place_assertion_triples(),
        )
