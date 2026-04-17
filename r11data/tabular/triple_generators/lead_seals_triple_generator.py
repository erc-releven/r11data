"""TripleGenerator for the Lead seals sheet."""

import itertools
from collections.abc import Iterator

from lodkit import _Triple, ttl
from r11data.tabular.models import LeadSeals
from r11data.tabular.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.utils.rdf_utils import crm, mkuri, r11spec, so, star
from rdflib import RDF, RDFS, URIRef


class LeadSealsRDFConverter(_ModelRDFConverter[LeadSeals]):
    def base_triples(self) -> Iterator[_Triple]:
        yield from ttl(
            self.model.seal_uri,
            (RDF.type, r11spec.Lead_Seal),
            (RDFS.label, f"{self.model.seal_id} (Seal ID)"),
        )

        if (external_url := self.model.external_url) is not None:
            yield (URIRef(str(external_url)), so.ID7_matches, self.model.seal_uri)

    def seal_collection_triples(self) -> Iterator[_Triple]:
        e13_crm_p46_uri = mkuri()

        return ttl(
            e13_crm_p46_uri,
            (RDF.type, star.E13_crm_P46),
            (
                crm.P140_assigned_attribute_to,
                ttl(
                    self.model.seal_collection_uri,
                    (RDF.type, crm.E78_Curated_Holding),
                    (RDFS.label, self.model.seal_collection),
                ),
            ),
            (crm.P141_assigned, self.model.seal_uri),
        )

    def __iter__(self) -> Iterator[_Triple]:
        ## the collection data in the table is currently incorrect;
        ## collection triple generation is therefore blocked/deferred
        return itertools.chain(self.base_triples(), self.seal_collection_triples())
