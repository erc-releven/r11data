"""TripleGenerator for the Author groups sheet."""

import itertools
from collections.abc import Iterator
from functools import cached_property

from lodkit import _Triple, ttl
from r11data.tabular.models import AuthorGroup, Person
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import crm, mkuri, r11spec
from rdflib import RDF, RDFS, URIRef


class AuthorGroupsRDFConverter(_ModelRDFConverter[AuthorGroup]):
    def base_triples(self) -> Iterator[_Triple]:
        group_member_model: Person | None = self.get_person_data(
            self.model.group_member, strict=False
        )

        if group_member_model is None:
            return

        group_member_uri: URIRef = group_member_model.person_uri

        yield from ttl(
            self.model.group_uri,
            (RDF.type, r11spec.Author_Group),
            (RDFS.label, self.model.group_identifier),
            (
                crm.P107_has_current_or_former_member,
                group_member_uri,
            ),
        )

    def __iter__(self) -> Iterator[_Triple]:
        return itertools.chain(self.base_triples())
