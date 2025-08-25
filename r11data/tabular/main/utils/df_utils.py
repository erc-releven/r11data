import pandas as pd


def check_sheets(io) -> None:
    """Parse an Excel sheet and check if all sheets can be loaded."""
    excel = pd.ExcelFile(io, engine="openpyxl")

    for sheet in excel.sheet_names:
        try:
            _ = pd.read_excel(io, sheet_name=sheet)
            print(f"ok: {sheet}")
        except Exception as e:
            print(f"exception: {sheet}: {e}")


def load_sheet(
    io, sheet_name: str, required_columns: list[str] | None = None
) -> pd.DataFrame:
    """Load an Excel file and prepare a sheet for processing."""

    def _filter_required(df):
        _required_columns = list() if required_columns is None else required_columns

        for column in _required_columns:
            df = df[df[column].astype(bool)]
        return df

    df = (
        pd.read_excel(io, sheet_name=sheet_name, dtype=str)
        .pipe(lambda df: df.where(pd.notna(df), None))  # cast NaN to None
        .pipe(lambda df: df.dropna(how="all"))  # drop all-None rows
        .pipe(_filter_required)  # filter rows with non-truthy required fields
    )

    assert isinstance(df, pd.DataFrame)  # type narrow
    return df


class SheetLoader:
    def __init__(self, io):
        self.io = io

    def load_persons_sheet(self) -> pd.DataFrame:
        return load_sheet(
            io=self.io, sheet_name="Persons", required_columns=["Identifier"]
        )

    def load_places_sheet(self) -> pd.DataFrame:
        return load_sheet(io=self.io, sheet_name="Places")

    def load_author_groups_sheet(self) -> pd.DataFrame:
        return load_sheet(io=self.io, sheet_name="Author groups")

    def load_text_publications_sheet(self) -> pd.DataFrame:
        return load_sheet(
            io=self.io,
            sheet_name="Text publications",
            required_columns=["Text identifier"],
        )
