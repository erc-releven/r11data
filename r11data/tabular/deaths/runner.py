"""Runner for R11data deaths conversions."""

from pathlib import Path
from typing import cast

from rdflib import Graph
from rich.console import Console

from r11data.abcs import _ABCRunner
from r11data.tabular.deaths.converters import (
    editor_converter_aa,
    editor_converter_mr,
    source_converter_aa,
    source_converter_mr,
)
from r11data.tabular.deaths.utils.namespaces import R11NamespaceManager
from r11data.utils.paths import output_tabular
from tabulardf import RowGraphConverter


converters: tuple[RowGraphConverter, ...] = (
    source_converter_aa,
    source_converter_mr,
    editor_converter_aa,
    editor_converter_mr,
)


class DeathsRunner(_ABCRunner):
    """Runner for deaths table conversions.

    Note: There is a known bug in tabulardf which causes RowGraphConverters
    to be inadvertently stateful between runs (RowGraphs are iadded to the interal graph object).
    The problem can be circumvented by calling a private RowGraphConverter method though.
    """

    def persist(self) -> None:
        """Run the conversion and persist the result in r11data/output."""
        graph = self.run()
        output_file = cast(Path, output_tabular / "deaths.ttl")

        with open(output_file, "w") as f:
            f.write(graph.serialize())

    def run(self) -> Graph:
        """Run the deaths table to RDF conversion."""
        graph = Graph()
        R11NamespaceManager(graph)

        for converter in converters:
            for row_graph in converter._generate_graphs():
                graph += row_graph

        return graph
