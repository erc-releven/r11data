"""Traversable constants for R11Data."""

from importlib.resources import files
from importlib.resources.abc import Traversable


r11data_base_path = files("r11data")

env_path = r11data_base_path / "../.env"

output: Traversable = files("r11data.output")

output_tabular: Traversable = output / "tabular"
output_starlegs: Traversable = output / "starlegs"

logs: Traversable = files("r11data") / "logs"
