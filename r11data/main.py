"""Entry point for r11data."""

import argparse
from types import SimpleNamespace

from loguru import logger
from r11data.starlegs.runner import StarlegsRunner
from r11data.tabular.deaths.runner import DeathsRunner


runners = SimpleNamespace()
runners.deaths = DeathsRunner()
runners.starlegs = StarlegsRunner()


parser = argparse.ArgumentParser(
    prog="R11Data",
    description="Invoke R11Data RDF generation runners.",
)

parser.add_argument("runner", choices=runners.__dict__.keys(), nargs="+")


if __name__ == "__main__":
    args: list[str] = parser.parse_args().__dict__["runner"]

    for arg in args:
        runner = getattr(runners, arg)
        logger.info(f"Invoking '{arg}' runner.")
        runner.persist()
