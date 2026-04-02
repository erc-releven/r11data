import json
from pathlib import Path

BASE = Path(__file__).parent if "__file__" in globals() else Path.cwd()


with (
    open(BASE / "pleiades.json") as pleiades,
    open(BASE / "geonames.json") as geonames,
    open(BASE / "wikidata.json") as wikidata,
):
    pleiades_json = {
        k: v
        for k, v in json.load(pleiades).items()
        if json.loads(v).get("coordinates") is not None
    }
    geonames_json = json.load(geonames)
    wikidata_json = json.load(wikidata)
