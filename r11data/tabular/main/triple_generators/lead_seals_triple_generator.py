"""TripleGenerator for the Lead seals sheet."""

from collections.abc import Iterator
from functools import cached_property
import itertools

from lodkit import _Triple, ttl
from r11data.tabular.main.models import LeadSeals
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import crm, mkuri, r11spec, so, star
from rdflib import RDF, RDFS, URIRef


class LeadSealsRDFConverter(_ModelRDFConverter[LeadSeals]):
    @cached_property
    def seal_uri(self) -> URIRef:
        return mkuri(self.model.seal_id)

    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.seal_uri,
            (RDF.type, r11spec.Lead_Seal),
            (RDFS.label, f"{self.model.seal_id} (Seal ID)"),
        )

        if (external_url := self.model.external_url) is not None:
            yield (URIRef(str(external_url)), so.ID7_matches, self.seal_uri)

    def seal_collection_triples(self) -> Iterator[_Triple]:
        seal_collection_uri = mkuri(self.model.seal_collection)
        e13_crm_p46_uri = mkuri()

        return ttl(
            e13_crm_p46_uri,
            (RDF.type, star.E13_crm_P46),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    seal_collection_uri,
                    (RDF.type, crm.E78_Curated_Holding),
                    (RDFS.label, self.model.seal_collection),
                ),
            ),
            (crm.P141_assigned, self.seal_uri),
        )

    def __iter__(self) -> Iterator[_Triple]:
        ## the collection data in the table is currently incorrect;
        ## collection triple generation is therefore blocked/deferred
        return itertools.chain(self.base_triples(), self.seal_collection_triples())
