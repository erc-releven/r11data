"""Custom types for starlegs functionality."""

from collections import UserString


class StarlegsQuery(UserString):
    """UserString which can hold additional metadata in a Namespace.

    Intended for Starlegs SPARQL queries.
    """

    def __init__(self, data: str, **metadata):
        self.data: str = data
        self.metadata: dict = metadata
