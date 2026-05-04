"""TripleGenerator for the Other objects sheet."""

from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import OtherObjects
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import aaao, crm, mkuri, star
from rdflib import RDF, RDFS


class OtherObjectsRDFConverter(_ModelRDFConverter[OtherObjects]):
    def base_triples(self) -> Iterator[_Triple]:
        self.object_uri = mkuri(self.model.title)

        yield from ttl(
            self.object_uri,
            (RDF.type, crm["Human-Made_Object"]),
            (RDFS.label, f"{self.model.title} (Label)"),
        )

        if (object_type := self.model.object_type) is not None:
            e17_uri = mkuri()

            yield from ttl(
                e17_uri,
                (RDF.type, crm.E17_Type_Assignment),
                (crm.P41_classified, self.object_uri),
                (
                    crm.P42_assigned,
                    ttl(
                        mkuri(object_type),
                        (RDF.type, crm.E55_Type),
                        (RDFS.label, f"{object_type} (Type)"),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e17_uri)

    # currently uses title as ID; better solution?
    def id_triples(self) -> Iterator[_Triple]:
        return ttl(
            mkuri(),
            (RDF.type, crm.E15_Identifier_Assignment),
            (crm.P140_assigned_attribute_to, self.object_uri),
            (
                crm.P37_assigned,
                ttl(
                    mkuri(),
                    (RDF.type, crm.E42_Identifier),
                    (crm.P190_has_symbolic_content, f"{self.model.title} (ID)"),
                ),
            ),
        )

    def object_creation_triples(self) -> Iterator[_Triple]:
        object_creation_uri = mkuri()

        # object creation: base event
        yield from ttl(
            mkuri(),
            (RDF.type, star.E13_crm_P108),
            (
                crm.P140_assigned_attribute_to,
                ttl(object_creation_uri, (RDF.type, crm.E12_Prodution)),
            ),
            (crm.P141_assigned, self.object_uri),
        )

        # object creation: timeframe assertion
        if (creation_date := self.model.creation_date) is not None:
            e13_crm_p4_uri = mkuri()

            yield from ttl(
                e13_crm_p4_uri,
                (RDF.type, star.E13_crm_P4),
                (crm.P140_assigned_attribute_to, object_creation_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm["E52_Time-Span"]),
                        (RDFS.label, creation_date),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e13_crm_p4_uri)

        if (creation_location := self.model.creation_location) is not None:
            e13_crm_p7_uri = mkuri()

            yield from ttl(
                e13_crm_p7_uri,
                (RDF.type, star.E13_crm_P7),
                (crm.P140_assigned_attribute_to, object_creation_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E27_Site),
                        (RDFS.label, creation_location),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e13_crm_p7_uri)

    # object creation: location assertion
    def locative_status_triples(self) -> Iterator[_Triple]:
        e13_aaao_zp83_uri, locative_status_uri = mkuri(), mkuri()

        # locative status: base event
        yield from ttl(
            e13_aaao_zp83_uri,
            (RDF.type, star.E13_aaao_ZP83),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    locative_status_uri, (RDF.type, aaao.ZE43_Physical_Locative_Status)
                ),
            ),
        )

        yield from self.authority_passage_triples(e13_aaao_zp83_uri)

        # locative status: location assertion
        if (documented_location := self.model.documented_location) is not None:
            e13_aaao_zp77_uri = mkuri()

            yield from ttl(
                e13_aaao_zp77_uri,
                (RDF.type, star.E13_aaao_ZP77),
                (crm.P140_assigned_attribute_to, locative_status_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E27_Site),
                        (RDFS.label, documented_location),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e13_aaao_zp77_uri)

        # locative status: timeframe assertion
        if (documented_date := self.model.documented_date) is not None:
            e13_crm_p4_uri = mkuri()

            yield from ttl(
                e13_crm_p4_uri,
                (RDF.type, star.E13_crm_P4),
                (crm.P140_assigned_attribute_to, locative_status_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm["E52_Time-Span"]),
                        (RDFS.label, documented_date),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e13_crm_p4_uri)

    def material_assertion_triples(self) -> Iterator[_Triple]:
        design_element = self.model.design_element
        material = self.model.material

        if design_element is None and material is None:
            return

        if design_element is not None:
            e13_crm_p65_uri = mkuri
            yield from ttl(
                e13_crm_p65_uri,
                (RDF.type, star.E13_crm_P65),
                (crm.P140_assigned_attribute_to, self.object_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E36_Visual_Item),
                        (RDFS.label, design_element),
                    ),
                ),
            )

            yield from self.authority_passage_triples(e13_crm_p65_uri)

        if material is not None:
            e13_crm_p45_uri = mkuri()

            yield from ttl(
                e13_crm_p45_uri,
                (RDF.type, star.E13_crm_P45),
                (crm.P140_assigned_attribute_to, self.object_uri),
                (
                    crm.P141_assigned,
                    ttl(mkuri(), (RDF.type, crm.E57_Material), (RDFS.label, material)),
                ),
            )

            yield from self.authority_passage_triples(e13_crm_p45_uri)

    def ownership_change_triples(self) -> Iterator[_Triple]:
        pass
