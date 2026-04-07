"""Pydantic-based Coordinate resolvers for Pleiades, GeoNames and Wikidata services."""

import logging

import httpx
from pydantic import AnyUrl, BaseModel, ConfigDict, computed_field, fields
from pydantic_extra_types.coordinate import Coordinate
from sparqlx import SPARQLWrapper

logger = logging.getLogger(__name__)


class _RemoteServiceCoordinates(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    url: AnyUrl

    @computed_field
    @property
    def id(self) -> str:
        return str(self.url).split("/")[-1]


class PleiadesCoordinates(_RemoteServiceCoordinates):
    @computed_field
    @property
    def coordinates(self) -> Coordinate | list[Coordinate] | None:
        try:
            response_json = httpx.get(
                f"https://pleiades.stoa.org/places/{self.id}/json"
            ).json()
        except Exception:
            print(f"Unable to resolve URI '{self.url}'.")
            return

        if not (features := response_json.get("features")):
            return None
        if not (geometry := features[0].get("geometry")):
            return None
        if not (coordinates := geometry.get("coordinates")):
            return None

        def _get_coordinates(
            coordinates,
        ):
            match coordinates:
                case (float(longitude), float(latitude)):
                    return Coordinate(latitude=latitude, longitude=longitude)  # pyright: ignore
                case ([float(), float()], *_):
                    return [_get_coordinates(coordinate) for coordinate in coordinates]
                case ([[float(), float()], *_], *_):
                    return [_get_coordinates(coordinate) for coordinate in coordinates]
                case _:
                    logger.warning("Undefined case in PleiadesCoordinates fetcher.")

        return _get_coordinates(coordinates=coordinates)


class GeoNamesCoordinates(_RemoteServiceCoordinates):
    @computed_field
    @property
    def coordinates(self) -> Coordinate | None:
        sparql_wrapper = SPARQLWrapper.from_rdf_source(
            f"https://www.geonames.org/{self.id}/about.rdf"
        )

        result = sparql_wrapper.query(
            """
            prefix wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>

            select ?latitude ?longitude
            where {
                [
                   wgs:lat ?latitude ;
                   wgs:long ?longitude
                ]
            }
            """,
            convert=True,
        )

        if result and (coordinates := result[0]):
            return Coordinate(
                **{k: float(v) for k, v in coordinates.items()}
            )  # float-cast values
        return None


class WikidataCoordinates(_RemoteServiceCoordinates):
    @computed_field
    @property
    def coordinates(self) -> Coordinate | None:
        query = f"""
        prefix wd: <http://www.wikidata.org/entity/>
        prefix wdt: <http://www.wikidata.org/prop/direct/>
        prefix geof: <http://www.opengis.net/def/function/geosparql/>

        select ?latitude ?longitude
        where {{
          wd:{self.id} wdt:P625 ?point .

          bind(geof:latitude(?point) as ?latitude) .
          bind(geof:longitude(?point) as ?longitude) .
        }}
        """
        sparql_wrapper = SPARQLWrapper("https://qlever.dev/api//wikidata")
        result = sparql_wrapper.query(query, convert=True)

        if result and (coordinates := result[0]):
            return Coordinate(**coordinates)
        return None
