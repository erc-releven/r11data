"""TripleGenerator for the Places sheet."""

import itertools
from collections.abc import Iterator
from functools import partial

from lodkit import _Triple, ttl
from pydantic import AnyUrl
from r11data.tabular.models import Place
from r11data.tabular.sources import geonames_json, pleiades_json
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.coordinates import serialize_coordinates
from r11data.tabular.utils.rdf_utils import crm, lrm, mkuri, star
from rdflib import RDF, RDFS, Literal, URIRef


class PlaceRDFConverter(_ModelRDFConverter[Place]):
    f11_pleiades_uri = URIRef("https://pleiades.stoa.org/")
    f11_geonames_uri = URIRef("https://www.geonames.org/")
    f11_wikidata_uri = URIRef("https://www.wikidata.org/")

    def base_triples(self) -> Iterator[_Triple]:
        return ttl(
            self.model.place_uri,
            (RDF.type, crm.E27_Site),
            (RDFS.label, self.model.reference_name),
        )

    def place_id_triples(self) -> Iterator[_Triple]:
        def _place_id_generator(
            place_id_uri: AnyUrl, place_id_service: URIRef
        ) -> Iterator[_Triple]:
            """Helper for generating Place ID assertions.

            place_id_uri is the place ID URI obtained from a service (Pleiades, Geonames, Wikidata).
            place_id_service is the Geo Data service (Pleiades, Geonames, Wikidata).
            """
            place_id_uri: URIRef = URIRef(str(place_id_uri))
            place_id_uri_str: str = str(place_id_uri)
            place_id_base: str = place_id_uri_str.split("/")[-1]

            return ttl(
                mkuri(
                    crm.E15_Identifier_Assignment,
                    self.model.reference_name,
                    place_id_service,
                ),
                (RDF.type, crm.E15_Identifier_Assignment),
                (crm.P140_assigned_attribute_to, self.model.place_uri),
                (crm.P14_carried_out_by, place_id_service),
                (
                    crm.P37_assigned,
                    ttl(
                        mkuri(
                            crm.E42_Identifier,
                            self.model.reference_name,
                            place_id_service,
                        ),
                        (RDF.type, crm.E42_Identifier),
                        (crm.P190_has_symbolic_content, place_id_base),
                    ),
                ),
            )

        if (pleiades_place_id_uri := self.model.pleiades_id) is not None:
            yield (self.f11_pleiades_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=pleiades_place_id_uri,
                place_id_service=self.f11_pleiades_uri,
            )

        if (geonames_place_id_uri := self.model.geonames_id) is not None:
            yield (self.f11_geonames_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=geonames_place_id_uri,
                place_id_service=self.f11_geonames_uri,
            )

        if (wikidata_place_id_uri := self.model.wikidata_id) is not None:
            yield (self.f11_wikidata_uri, RDF.type, lrm.F11_Corporate_Body)
            yield from _place_id_generator(
                place_id_uri=wikidata_place_id_uri,
                place_id_service=self.f11_wikidata_uri,
            )

    def part_of_place_triples(self) -> Iterator[_Triple]:
        if (incorporated_place := self.model.incorporates_place) is None:
            return

        incorporated_place_model = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=incorporated_place,
            strict=False,
        )

        if incorporated_place_model is None:
            return

        e13_crm_p89_uri = mkuri()

        yield from ttl(
            e13_crm_p89_uri,
            (RDF.type, star.E13_crm_P89),
            (crm.P140_assigned_attribute_to, self.model.place_uri),
            (crm.P141_assigned, incorporated_place_model.place_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p89_uri)

    def place_type_triples(self) -> Iterator[_Triple]:
        if (place_type := self.model.place_type) is None:
            return

        e17_uri = mkuri()
        place_type_uri = mkuri("Place type", place_type)

        yield from ttl(
            e17_uri,
            (RDF.type, crm.E17_Type_Assignment),
            (crm.P41_classified, self.model.place_uri),
            (
                crm.P42_assigned,
                ttl(place_type_uri, (RDF.type, crm.E55_Type), (RDFS.label, place_type)),
            ),
        )

        ## todo: investigate
        # authority + passage triples
        yield from self.authority_passage_triples(e17_uri)

    def place_succession_triples(self) -> Iterator[_Triple]:
        if (place_succession := self.model.succeeds_place) is None:
            return

        place_succession_model = self.lookup(
            sheet=self.sheets.places,
            model=Place,
            column="Reference name",
            key=place_succession,
            strict=False,
        )

        if place_succession_model is None:
            return

        e13_spec_l3_uri = mkuri()

        yield from ttl(
            e13_spec_l3_uri,
            (RDF.type, star.E13_spec_L3),
            (crm.P140_assigned_attribute_to, self.model.place_uri),
            (crm.P141_assigned, place_succession_model.place_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_spec_l3_uri)

    def place_population_triples(self) -> Iterator[_Triple]:
        if (population_group := self.model.had_population_group) is None:
            return

        e13_crm_p53_uri = mkuri()

        yield from ttl(
            e13_crm_p53_uri,
            (RDF.type, star.E13_crm_P53),
            (
                crm.P140_assigned_attribute_to,
                mkuri("Population label", population_group),
            ),
            (crm.P141_assigned, self.model.place_uri),
        )

        # authority + passage triples
        yield from self.authority_passage_triples(e13_crm_p53_uri)

    def spatio_temporal_existence_triples(self) -> Iterator[_Triple]:
        e92_base_uri = mkuri()
        coordinates, begin, end = map(
            partial(getattr, self.model),
            ["location_coordinates", "earliest_existence", "latest_existence"],
        )

        def spatio_temporal_base_triples() -> Iterator[_Triple]:
            e13_crm_p196_uri: URIRef = mkuri()

            return ttl(
                e13_crm_p196_uri,
                (RDF.type, star.E13_crm_P196),
                (crm.P140_assigned_attribute_to, self.model.place_uri),
                (
                    crm.P141_assigned,
                    ttl(e92_base_uri, (RDF.type, crm.E92_Spacetime_Volume)),
                ),
                (crm.P14_carried_out_by, self.model.service),
            )

        def spatio_temporal_base_coordinates_tripes() -> Iterator[_Triple]:
            if coordinates is None:
                return

            e13_crm_p161_uri: URIRef = mkuri()

            yield from ttl(
                e13_crm_p161_uri,
                (RDF.type, star.E13_crm_P161),
                (crm.P140_assigned_attribute_to, e92_base_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E53_Place),
                        (
                            crm.P53i_is_former_or_current_location_of,
                            self.model.place_uri,
                        ),
                        (
                            crm.P168_place_is_defined_by,
                            Literal(
                                serialize_coordinates(coordinates), datatype=RDF.JSON
                            ),
                        ),
                    ),
                ),
                (crm.P14_carried_out_by, self.model.service),
            )

        def temporal_triples() -> Iterator[_Triple]:
            """Note: Temporal references are currently not translated to Julian days.

            Currently, `Earliest existence` and `Latest existence` fields are never defined,
            so this is actually not relevant; if those fields ever were defined, one would
            need to see if existing Julian day converters are able to convert whatever data
            is defined in the table fields.
            """

            e52_uri: URIRef = mkuri()
            e13_crm_p160_uri: URIRef = mkuri()

            yield from ttl(
                e13_crm_p160_uri,
                (RDF.type, star.E13_crm_P160),
                (crm.P140_assigned_attribute_to, e92_base_uri),
                (crm.P141_assigned, ttl(e52_uri, (RDF.type, crm["E52_Time-Span"]))),
            )

            if begin or end:
                label = f"{begin or ''} - {end or ''}".strip()
                yield (e52_uri, RDFS.label, Literal(label))

            if begin is not None:
                yield (e52_uri, crm.P82a_begin_of_the_begin, Literal(begin))

            if end is not None:
                yield (e52_uri, crm.P82b_end_of_the_end, Literal(end))

            # authority + passage triples
            yield from self.authority_passage_triples(e13_crm_p160_uri)

        def _assert_coordinates(
            coordinates_json: bytes, authority_uri: URIRef | None = None
        ) -> Iterator[_Triple]:
            """Helper for _spatio_definition_triples generator."""

            e27_uri: URIRef = mkuri(self.model.reference_name, str(authority_uri))
            e92_uri: URIRef = mkuri()

            yield (e92_uri, RDF.type, crm.E92_Spacetime_Volume)

            yield from ttl(
                mkuri(),
                (RDF.type, star.E13_so_ID8),
                (
                    crm.P140_assigned_attribute_to,
                    ttl(e27_uri, (RDF.type, crm.E27_Site)),
                ),
                (crm.P141_assigned, self.model.place_uri),
                (crm.P14_carried_out_by, self.model.service),
            )

            yield from ttl(
                mkuri(),
                (RDF.type, star.E13_crm_P196),
                (crm.P140_assigned_attribute_to, e27_uri),
                (crm.P141_assigned, e92_uri),
                (crm.P14_carried_out_by, authority_uri),
            )

            yield from ttl(
                mkuri(),
                (RDF.type, star.E13_crm_P161),
                (crm.P140_assigned_attribute_to, e92_uri),
                (
                    crm.P141_assigned,
                    ttl(
                        mkuri(),
                        (RDF.type, crm.E53_Place),
                        (crm.P53i_is_former_or_current_location_of, e27_uri),
                        (
                            crm.P168_place_is_defined_by,
                            Literal(coordinates_json, datatype=RDF.JSON),
                        ),
                    ),
                ),
            )

        def spatial_triples() -> Iterator[_Triple]:
            if (pleiades_id := self.model.pleiades_id) is not None:
                coordinates_json = pleiades_json.get(pleiades_id)  # pyright: ignore

                if coordinates_json:
                    yield from _assert_coordinates(
                        coordinates_json=coordinates_json,
                        authority_uri=self.f11_pleiades_uri,
                    )

            if (geonames_id := self.model.geonames_id) is not None:
                coordinates_json = geonames_json.get(geonames_id)

                if coordinates_json:
                    yield from _assert_coordinates(
                        coordinates_json=coordinates_json,
                        authority_uri=self.f11_geonames_uri,
                    )

            if (wikidata_id := self.model.wikidata_id) is not None:
                coordinates_json = geonames_json.get(wikidata_id)

                if coordinates_json:
                    yield from _assert_coordinates(
                        coordinates_json=coordinates_json,
                        authority_uri=self.f11_wikidata_uri,
                    )

        return itertools.chain(
            spatio_temporal_base_triples(),
            spatio_temporal_base_coordinates_tripes(),
            temporal_triples(),
            spatial_triples(),
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
