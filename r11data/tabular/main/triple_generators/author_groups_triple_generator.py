"""TripleGenerator for the Author groups sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools
import logging

from lodkit import _Triple, ttl
from r11data.tabular.main.models import AuthorGroup, Person
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, r11spec
from rdflib import RDF, RDFS, URIRef


class AuthorGroupsRDFConverter(_ModelRDFConverter[AuthorGroup]):
    @cached_property
    def group_uri(self):
        group_uri = (
            mkuri(self.model.group_identifier)
            if (_wisski_id := self.model.wisski_id) is None
            else URIRef(str(_wisski_id))
        )

        return group_uri

    def base_triples(self) -> Iterator[_Triple]:
        group_member_model: Person | None = self.get_person_data(
            self.model.group_member, strict=False
        )

        if group_member_model is None:
            return

        group_member_uri: URIRef = group_member_model.person_uri

        yield from ttl(
            self.group_uri,
            (RDF.type, r11spec.Author_Group),
            (RDFS.label, self.model.group_identifier),
            (
                crm.P107_has_current_or_former_member,
                group_member_uri,
            ),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(self.base_triples())
