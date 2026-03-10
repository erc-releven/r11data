"""Convert sources to xlsx."""

from pathlib import Path

import pandas as pd


for csv in Path(".").glob("*.csv"):
    df = pd.read_csv(csv)
    df.to_excel(csv.with_suffix(".xlsx"), index=False)
