"""TripleGenerator for the Places sheet."""

from collections.abc import Iterator
from functools import cached_property, partial
import itertools

from lodkit import _Triple, ttl
from pydantic import AnyUrl
from r11data.tabular.main.models import Place
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, lrm, mkuri, star
from rdflib import Literal, OWL, RDF, RDFS, URIRef


class PlaceRDFConverter(_ModelRDFConverter[Place]):
    @cached_property
    def place_uri(self) -> URIRef:
        return mkuri(self.model.reference_name)

    def base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.place_uri,
            (RDF.type, crm.E27_Site),
            (RDFS.label, self.model.reference_name),
        )

    def place_id_triples(self) -> Iterator[_Triple]:
        def _place_id_generator(
            place_id_uri: AnyUrl, id_source: URIRef
        ) -> Iterator[_Triple]:
            e42_uri = mkuri()

            place_id_uri_str: str = str(place_id_uri)
            place_id_base = place_id_uri_str.split("/")[-1]
            assert place_id_base

            return ttl(
                mkuri(),
                (RDF.type, crm.E15_Identifier_Assignment),
                (crm.P140_assigned_attribute_to, self.place_uri),
                (crm.P14_carried_out_by, id_source),
                (
                    crm.P37_assigned,
                    ttl(
                        e42_uri,
                        (RDF.type, crm.E42_Identifier),
                        (crm.P190_has_symbolic_content, place_id_base),
                        (OWL.sameAs, URIRef(place_id_uri_str)),
                    ),
                ),
            )

        if (pleiades_place_id_uri := self.model.pleiades_id) is not None:
            f11_pleiades_uri = mkuri()

            yield (f11_pleiades_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=pleiades_place_id_uri, id_source=f11_pleiades_uri
            )

        if (geonames_place_id_uri := self.model.geonames_id) is not None:
            f11_geonames_uri = mkuri()

            yield (f11_geonames_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=geonames_place_id_uri, id_source=f11_geonames_uri
            )

        if (wikidata_place_id_uri := self.model.wikidata_id) is not None:
            f11_wikidata_uri = mkuri()

            yield (f11_wikidata_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=wikidata_place_id_uri, id_source=f11_wikidata_uri
            )

    def part_of_place_triples(self) -> Iterator[_Triple]:
        if (incorporated_place := self.model.incorporates_place) is None:
            return

        e13_crm_p89_uri = mkuri()

        yield from ttl(
            e13_crm_p89_uri,
            (RDF.type, star.E13_crm_P89),
            (crm.P140_assigned_attribute_to, self.place_uri),
            (crm.P141_assigned, mkuri(incorporated_place)),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p89_uri)

    def place_type_triples(self) -> Iterator[_Triple]:
        if (place_type := self.model.place_type) is None:
            return

        e17_uri = mkuri()
        place_type_uri = mkuri(place_type)

        yield from ttl(
            e17_uri,
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P41_classified, self.place_uri),
            (
                crm.P42_assigned,
                ttl(place_type_uri, (RDF.type, crm.E55_Type), (RDFS.label, place_type)),
            ),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e17_uri)

    def place_succession_triples(self) -> Iterator[_Triple]:
        if (place_succession := self.model.succeeds_place) is None:
            return

        e13_spec_l3_uri = mkuri()

        yield from ttl(
            e13_spec_l3_uri,
            (RDF.type, star.E13_spec_L3),
            (crm.P140_assigned_attribute_to, self.place_uri),
            # no lookup needed, place URI is hashed
            (crm.P141_assigned, mkuri(place_succession)),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_spec_l3_uri)

    def place_population_triples(self) -> Iterator[_Triple]:
        if (population_group := self.model.had_population_group) is None:
            return

        e13_crm_p53 = mkuri()

        yield from ttl(
            e13_crm_p53,
            (RDF.type, star.E13_crm_P53),
            (crm.P140_assigned_attribute_to, population_group),
            (crm.P141_assigned, self.place_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p53)

    def spatio_temporal_existence_triples(self) -> Iterator[_Triple]:
        e92_uri = mkuri()
        coordinates, begin, end = map(
            partial(getattr, self.model),
            ["location_coordinates", "earliest_existence", "latest_existence"],
        )

        def _spatio_temporal_base_triples() -> Iterator[_Triple]:
            if not any([coordinates, begin, end]):
                return

            e13_crm_p196_uri = mkuri()
            yield from ttl(
                e13_crm_p196_uri,
                (RDF.type, star.E13_crm_P196),
                (crm.P140_assigned_attribute_to, self.place_uri),
                (crm.P141_assigned, ttl(e92_uri, (RDF.type, crm.E92_Spacetime_Volume))),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_crm_p196_uri)

        def _temporal_begin_end_triples() -> Iterator[_Triple]:
            e52_uri = mkuri()
            e13_crm_p160_uri = mkuri()

            yield from ttl(
                e13_crm_p160_uri,
                (RDF.type, star.E13_crm_P160),
                (crm.P140_assigned_attribute_to, e92_uri),
                (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
            )

            if begin or end:
                label = f"{begin or ''} - {end or ''}".strip()
                yield (e13_crm_p160_uri, RDFS.label, Literal(label))

            if begin is not None:
                yield (e13_crm_p160_uri, crm.P82a_begin_of_the_begin, Literal(begin))

            if end is not None:
                yield (e13_crm_p160_uri, crm.P82b_end_of_the_end, Literal(end))

            # authority + passage triples
            yield from self.authority_passage_triples(e13_crm_p160_uri)

        def _spatio_definition_triples() -> Iterator[_Triple]:
            if coordinates is None:
                return

            e13_crm_p161_uri = mkuri()

            yield from ttl(
                e13_crm_p161_uri,
                (RDF.type, star.E13_crm_P161),
                (crm.P140_assigned_attribute_to, e92_uri),
                (
                    crm.P141_assigned,
                    [
                        (RDF.type, crm.E53_Place),
                        (
                            crm.P168_place_is_defined_by,
                            str(coordinates),
                        ),
                    ],
                ),
            )

            # authority + passage triples
            yield from self.authority_passage_triples(e13_crm_p161_uri)

        return itertools.chain(
            _spatio_temporal_base_triples(),
            _temporal_begin_end_triples(),
            _spatio_definition_triples(),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(
            self.base_triples(),
            self.place_id_triples(),
            self.part_of_place_triples(),
            self.place_type_triples(),
            self.place_succession_triples(),
            self.place_population_triples(),
            self.spatio_temporal_existence_triples(),
        )
