"""Traversable constants for R11Data."""

from importlib.resources import files
from importlib.resources.abc import Traversable


output: Traversable = files("r11data.output")

output_tabular: Traversable = output / "tabular"
output_starlegs: Traversable = output / "starlegs"

logs: Traversable = files("r11data") / "logs"
