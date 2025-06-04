"""Runner for R11data Kekaumenos data extraction and generation."""

from collections.abc import Iterator
from collections.abc import Callable
import csv
from functools import partial
import json
import re
from typing import Annotated
from typing import Any

from jinja2 import Template
from r11data.kekaumenos.models import KekaumenosSAWSDataField, KekaumenosSAWSModel
from r11data.kekaumenos.sparql.kekaumenos_queries import (
    kekaumenos_eng_query,
    kekaumenos_grc_query,
)
from r11data.kekaumenos.utils.utils import (
    get_bindings_from_response,
    group_iterator,
    httpx_run_sparql_query,
    strip_xml_nodes,
)
from r11data.utils.paths import data_kekaumenos
import toolz


kekaumenos_components: Annotated[
    list[Callable[[Any], Iterator]], "Compose stack for Kekaumenous data extraction."
] = [
    partial(group_iterator, by="object"),
    strip_xml_nodes,
    get_bindings_from_response,
    httpx_run_sparql_query,
]


def generate_kekaumenos_models(query: str) -> Iterator[KekaumenosSAWSModel]:
    """Query the SAWS store and instantiate KekaumenosSAWSModel instances from the SPARQL response."""
    kekaumenos_compose = toolz.compose(*kekaumenos_components)(
        endpoint="https://ancientwisdoms.ac.uk/sesame/repositories/saws", query=query
    )
    for node_id, data in kekaumenos_compose.items():
        yield KekaumenosSAWSModel(node_id=node_id, data=KekaumenosSAWSDataField(**data))


def persist_kekaumenos_json_to_file(
    models: Iterator[KekaumenosSAWSModel], file_name: str
) -> None:
    """Persist KekaumenosSAWSModel JSON to a file."""
    with open(data_kekaumenos / file_name, "w") as f:  # type: ignore
        json_data = [model.model_dump() for model in models]
        f.write(json.dumps(json_data, indent=4, ensure_ascii=False))


def persist_saws_kekaumenos() -> None:
    """Run Kekaumenos JSON persistance."""
    persist_kekaumenos_json_to_file(
        generate_kekaumenos_models(kekaumenos_eng_query), "kekaumenos_eng.json"
    )

    persist_kekaumenos_json_to_file(
        generate_kekaumenos_models(kekaumenos_grc_query), "kekaumenos_grc.json"
    )


def get_releven_kekaumenos_bindings():
    query = """
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX spec: <https://r11.eu/ns/spec/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX star: <https://r11.eu/ns/star/>

    select distinct ?e33 ?text ?label
    where {
    ?a crm:P141_assigned [a spec:Text_Expression ; rdfs:label "Consilia et narrationes"];
       a star:E13_lrmoo_R76 ;
       crm:P140_assigned_attribute_to ?pub .
    ?b crm:P140_assigned_attribute_to ?pub ;
       a star:E13_lrmoo_R15 ;
       crm:P141_assigned ?e33 .
    ?c ^crm:P67_refers_to ?e33 ;
       a [rdfs:subClassOf crm:E13_Attribute_Assignment] .
    ?e33 a crm:E33_Linguistic_Object ;
        crm:P190_has_symbolic_content ?text ;
        rdfs:label ?label.

    filter (?text != "")
    }
    """

    response = httpx_run_sparql_query(
        endpoint="https://graphdb.r11.eu/repositories/RELEVEN_2025", query=query
    )
    bindings = get_bindings_from_response(response)

    return bindings


def get_saws_bindings():
    with open(data_kekaumenos / "kekaumenos_grc.json") as f:  # type: ignore
        for binding in json.loads(f.read()):
            yield {
                "saws_uri": binding["node_id"],
                "saws_text": binding["data"]["has_text_content"],
            }


def generate_matches():
    for r11_binding in get_releven_kekaumenos_bindings():
        r11_uri, r11_text, r11_label = r11_binding.values()

        for saws_binding in get_saws_bindings():
            saws_uri, saws_text = saws_binding.values()

            if r11_text in saws_text:
                yield {
                    "r11_uri": r11_uri,
                    "r11_text": r11_text,
                    "r11_label": r11_label,
                    "saws_uri": saws_uri,
                    "saws_text": saws_text,
                }


def color_match(saws_text, match):
    pattern = re.compile(re.escape(match), re.IGNORECASE)
    return pattern.sub(r'<span style="color: red">\g<0></span>', saws_text)


with open("./template.html") as template, open("./matches.html", "w") as output:
    template = Template(template.read())
    rendered = template.render(data=list(generate_matches()), color_match=color_match)

    output.write(rendered)


with open("./matches.csv", "w") as csvfile:
    fieldnames = ["r11_uri", "r11_text", "r11_label", "saws_uri", "saws_text"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(generate_matches())
