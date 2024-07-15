"""Dataframe partitions."""

import importlib.resources

import pandas as pd


xlsx_path = importlib.resources.files("r11data.tabular.deaths.tables.xlsx")

dataframe_aa = pd.read_excel(xlsx_path / "c11deaths-AA.xlsx")
dataframe_mr = pd.read_excel(xlsx_path / "c11deaths-MR.xlsx")

source_partition_aa = dataframe_aa.loc[dataframe_aa["Dating authority"] == "Source"]

source_partition_mr = dataframe_mr.loc[
    dataframe_mr["Dating authority"] == "source"  # lowercase!
]

editor_partition_aa = dataframe_aa.loc[dataframe_aa["Dating authority"] == "Editor"]

editor_partition_mr = dataframe_mr.loc[
    dataframe_mr["Dating authority"] == "editor"  # lowercase!
]
