"""Script for Places sheet JSON coordinate generation."""

import itertools
import json
from functools import partial
from pathlib import Path

from pydantic import AnyUrl
from r11data.tabular.models import Place
from r11data.tabular.utils.coordinates import (
    GeoNamesCoordinates,
    PleiadesCoordinates,
    WikidataCoordinates,
    _RemoteServiceCoordinates,
)
from r11data.tabular.utils.df_utils import Sheets
from r11data.tabular.utils.paths import tabular_main_sources_path
from r11data.tabular.utils.rdf_utils import (
    aleks_uri,
    lewis_uri,
    marton_uri,
)

lewis_sheets = Sheets(
    owner_id=lewis_uri,
    io=tabular_main_sources_path / "lewis.xlsx",
)

aleks_sheets = Sheets(
    owner_id=aleks_uri,
    io=tabular_main_sources_path / "aleks.xlsx",
)

marton_sheets = Sheets(
    owner_id=marton_uri,
    io=tabular_main_sources_path / "marton.xlsx",
)


def _serialize(
    coordinate_model: type[_RemoteServiceCoordinates],
    url: AnyUrl,
) -> str | None:
    coord = coordinate_model(url=url)
    try:
        return coord.model_dump_json(include={"coordinates"})
    except Exception as exc:
        print(f"Serialization error for {url}: {exc}")
        return None


serialize_geonames = partial(_serialize, coordinate_model=GeoNamesCoordinates)
serialize_pleiades = partial(_serialize, coordinate_model=PleiadesCoordinates)
serialize_wikidata = partial(_serialize, coordinate_model=WikidataCoordinates)


def iter_place_rows():
    yield from itertools.chain(
        lewis_sheets.places.iterrows(),
        aleks_sheets.places.iterrows(),
        marton_sheets.places.iterrows(),
    )


def generate_coordinate_json(
    *,
    id_attr: str,
    serializer,
    output_file: str | Path,
) -> None:
    coordinate_json: dict[str, str | None] = {}

    for n, row in iter_place_rows():
        print(f"Processing line: {n}")

        model = Place(**row.to_dict())
        place_id = getattr(model, id_attr)

        if place_id is None:
            continue

        coordinate_json[place_id] = serializer(url=place_id)

    Path(output_file).write_text(json.dumps(coordinate_json), encoding="utf-8")


def generate_geonames_json() -> None:
    generate_coordinate_json(
        id_attr="geonames_id",
        serializer=serialize_geonames,
        output_file="./geonames.json",
    )


def generate_wikidata_json() -> None:
    generate_coordinate_json(
        id_attr="wikidata_id",
        serializer=serialize_wikidata,
        output_file="./wikidata.json",
    )


def generate_pleiades_json() -> None:
    generate_coordinate_json(
        id_attr="pleiades_id",
        serializer=serialize_pleiades,
        output_file="./pleiades.json",
    )


# generate_geonames_json()
generate_pleiades_json()
# generate_wikidata_json()
