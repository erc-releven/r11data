from functools import cached_property
import re

import pandas as pd
from rdflib import URIRef


class Sheets:
    def __init__(self, owner_id: URIRef, io, check: bool = False):
        self.owner_id = owner_id
        self.io = io

        if check:
            self.check_sheets()

    @cached_property
    def persons(self) -> pd.DataFrame:
        return self.load_sheet(
            sheet_name="Persons",
            required_columns=["Identifier"],
        )

    @cached_property
    def places(self) -> pd.DataFrame:
        return self.load_sheet(sheet_name="Places")

    @cached_property
    def author_groups(self) -> pd.DataFrame:
        return self.load_sheet(sheet_name="Author groups")

    @cached_property
    def actor_groups(self) -> pd.DataFrame:
        return self.load_sheet(sheet_name="Actor groups")

    @cached_property
    def text_publications(self) -> pd.DataFrame:
        return self.load_sheet(
            sheet_name="Text publications",
            required_columns=["Text identifier"],
        )

    def load_sheet(
        self, sheet_name: str, required_columns: list[str] | None = None
    ) -> pd.DataFrame:
        """Load an Excel file and prepare a sheet for processing."""

        def _filter_required(df: pd.DataFrame) -> pd.DataFrame:
            _required_columns = list() if required_columns is None else required_columns

            for column in _required_columns:
                df = df[df[column].astype(bool)]
            return df

        def _clean_whitespace(df: pd.DataFrame) -> pd.DataFrame:
            df_cleaned = df.copy()

            for col in df_cleaned.columns:
                if df_cleaned[col].dtype == "object":
                    df_cleaned[col] = df_cleaned[col].apply(
                        lambda x: re.sub(r"\s+", " ", str(x).strip())
                        if pd.notna(x) and x is not None
                        else x
                    )

            return df_cleaned

        df = (
            pd.read_excel(self.io, sheet_name=sheet_name, dtype=str, engine="calamine")
            .pipe(lambda df: df.where(pd.notna(df), None))  # cast NaN to None
            .pipe(lambda df: df.dropna(how="all"))  # drop all-None rows
            .pipe(_filter_required)  # filter rows with non-truthy required fields
            .pipe(_clean_whitespace)  # sanitize whitespace
        )

        assert isinstance(df, pd.DataFrame)  # type narrow
        return df

    def check_sheets(self) -> None:
        """Parse an Excel sheet and check if all sheets can be loaded."""
        excel = pd.ExcelFile(self.io, engine="openpyxl")

        for sheet in excel.sheet_names:
            try:
                _ = pd.read_excel(self.io, sheet_name=sheet)
                print(f"ok: {sheet}")
            except Exception as e:
                print(f"exception: {sheet}: {e}")
