"""TabulaRDF Converters for R11."""

from r11data.tabular.deaths.rules import (
    aa_editor_row_rule,
    mr_editor_row_rule,
    source_row_rule,
)
from r11data.tabular.deaths.tables.partitions import (
    editor_partition_aa,
    editor_partition_mr,
    source_partition_aa,
    source_partition_mr,
)
from tabulardf import RowGraphConverter


source_converter_aa = RowGraphConverter(
    dataframe=source_partition_aa,
    row_rule=source_row_rule,
)

source_converter_mr = RowGraphConverter(
    dataframe=source_partition_mr,
    row_rule=source_row_rule,
)

editor_converter_aa = RowGraphConverter(
    dataframe=editor_partition_aa,
    row_rule=aa_editor_row_rule,
)

editor_converter_mr = RowGraphConverter(
    dataframe=editor_partition_mr,
    row_rule=mr_editor_row_rule,
)
