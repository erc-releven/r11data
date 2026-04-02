"""Convert sources to xlsx."""

from pathlib import Path

import pandas as pd


for csv in Path(".").glob("*.csv"):
    df = pd.read_csv(csv)

    # remove rows that do not specify presence
    df = df[df["RELEVEN location type"].str.contains("Specifies presence", na=False)]

    df.to_excel(csv.with_suffix(".xlsx"), index=False)
