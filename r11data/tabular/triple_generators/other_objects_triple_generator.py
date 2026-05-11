"""TripleGenerator for the Other objects sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import OtherObjects, Place, TextPublication
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.date_parser import generate_date_triples
from r11data.tabular.utils.rdf_utils import (
    aaao,
    crm,
    mkuri,
    star,
)
from rdflib import RDF, RDFS, URIRef


class OtherObjectsRDFConverter(_ModelRDFConverter[OtherObjects]):
    """Note: The class currently does not define generators for

    - locative Status assertions,
    - ownership change,
    - commission
    - decoration material
    - design element

    Those data points do not clearly map to the currently defined model
    and/or are not clear to me conceptually.
    """

    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.object_uri,
            (RDF.type, crm["E22_Human-Made_Object"]),
            (RDFS.label, f"{self.model.title}"),
        )

    def object_type_assertion_triples(self) -> Iterator[_Triple]:
        if (object_type := self.model.object_type) is None:
            return

        e17_uri = mkuri()

        yield from ttl(
            e17_uri,
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P41_classified, self.model.object_uri),
            (
                crm.P42_assigned,
                ttl(
                    mkuri("Object type", object_type),  # hashed according to policy
                    (RDF.type, crm.E55_Type),
                    (RDFS.label, object_type),
                ),
            ),
        )

    def external_id_triples(self) -> Iterator[_Triple]:
        if (external_id := self.model.external_id) is None:
            return

        yield from ttl(
            mkuri(),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P140_assigned_attribute_to, self.model.object_uri),
            (
                crm.P37_assigned,
                ttl(
                    mkuri(crm.E42_Identifier, str(external_id), "https://r11.eu/"),
                    (RDF.type, crm.E42_Identifier),
                    (
                        crm.P190_has_symbolic_content,
                        f"{self.model.title} (External ID)",
                    ),
                ),
            ),
            (crm.P14_carried_out_by, URIRef("https://r11.eu")),
        )

    def object_creation_triples(self) -> Iterator[_Triple]:
        e13_crm_p108_uri = mkuri()

        yield from ttl(
            e13_crm_p108_uri,
            (RDF.type, star.E13_crm_P108),
            (
                crm.P140_assigned_attribute_to,
                ttl(self.model.object_production_uri, (RDF.type, crm.E12_Production)),
            ),
            (crm.P141_assigned, self.model.object_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p108_uri)

    def object_creation_time_assertion_triples(self) -> Iterator[_Triple]:
        if (creation_date := self.model.creation_date) is None:
            return

        e13_crm_p4_uri = mkuri()
        e52_uri = mkuri()

        yield from ttl(
            e13_crm_p4_uri,
            (RDF.type, star.E13_crm_P4),
            (crm.P140_assigned_attribute_to, self.model.object_production_uri),
            (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
        )

        yield from generate_date_triples(e52_uri, creation_date)
        yield from self.authority_passage_triples(e13_crm_p4_uri)

    def object_creation_location_assertion_triples(self) -> Iterator[_Triple]:
        if (creation_location := self.model.creation_location) is None:
            return

        creation_location_model: Place | None = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=creation_location,
            strict=False,
        )

        if creation_location_model is None:
            return

        e13_crm_p7_uri = mkuri()

        yield from ttl(
            e13_crm_p7_uri,
            (RDF.type, star.E13_crm_P7),
            (crm.P140_assigned_attribute_to, self.model.object_production_uri),
            (crm.P141_assigned, creation_location_model.place_uri),
        )

        yield from self.authority_passage_triples(e13_crm_p7_uri)

    def material_assertion_triples(self) -> Iterator[_Triple]:
        if (material := self.model.material) is None:
            return

        e13_crm_p45_uri = mkuri()

        yield from ttl(
            e13_crm_p45_uri,
            (RDF.type, star.E13_crm_P45),
            (crm.P140_assigned_attribute_to, self.model.object_uri),
            (
                crm.P141_assigned,
                ttl(
                    mkuri("Material", material),
                    (RDF.type, crm.E57_Material),
                    (RDFS.label, material),
                ),
            ),
        )

        yield from self.authority_passage_triples(e13_crm_p45_uri)

    def bears_text_assertion_triples(self) -> Iterator[_Triple]:
        if (bears_text := self.model.bears_text) is None:
            return

        bears_text_model: TextPublication | None = self.lookup(
            sheet=self.sheets.text_publications,
            model=TextPublication,
            column="Text identifier",
            key=bears_text,
            strict=False,
        )

        if bears_text_model is None:
            return

        e13_crm_128_uri = mkuri()

        yield from ttl(
            e13_crm_128_uri,
            (RDF.type, star.E13_crm_P128),
            (crm.P140_assigned_attribute_to, self.model.object_uri),
            (crm.P141_assigned, bears_text_model.text_expression_uri),
        )

        yield from self.authority_passage_triples(e13_crm_128_uri)

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.object_type_assertion_triples(),
            self.external_id_triples(),
            self.object_creation_triples(),
            self.object_creation_time_assertion_triples(),
            self.object_creation_location_assertion_triples(),
            self.material_assertion_triples(),
            self.bears_text_assertion_triples(),
        )
