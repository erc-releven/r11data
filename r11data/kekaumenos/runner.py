"""Runner for R11data Kekaumenos data extraction and generation."""

from collections.abc import Iterator
from collections.abc import Callable
from functools import partial
import json
from typing import Annotated
from typing import Any

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
        for model in models:
            f.write(json.dumps(model.model_dump(), indent=4, ensure_ascii=False))


def persist_kekaumenos() -> None:
    """Run Kekaumenos JSON persistance."""
    persist_kekaumenos_json_to_file(
        generate_kekaumenos_models(kekaumenos_eng_query), "kekaumenos_eng.json"
    )

    persist_kekaumenos_json_to_file(
        generate_kekaumenos_models(kekaumenos_grc_query), "kekaumenos_grc.json"
    )


if __name__ == "__main__":
    persist_kekaumenos()
