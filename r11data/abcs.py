"""ABCs for R11Data."""

from abc import ABC, abstractmethod

from rdflib import Graph


class _ABCRunner(ABC):
    """ABC for R11Data Runners."""

    @abstractmethod
    def persist(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> Graph:
        raise NotImplementedError
