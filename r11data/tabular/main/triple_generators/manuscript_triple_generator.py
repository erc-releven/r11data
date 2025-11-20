"""TripleGenerator for the Manuscripts sheet."""

from collections.abc import Iterable, Iterator
from functools import cached_property
import itertools
from typing import cast

from lodkit import _Triple, ttl
from r11data.tabular.main.models import Manuscript
from r11data.tabular.main.triple_generators.bases import _ModelRDFConverter
from r11data.tabular.main.utils.rdf_utils import (
    crm,
    get_source_name_lang_tag,
    lrm,
    mkuri,
    r11,
    r11pros,
    r11spec,
    star,
)
from rdflib import Literal, RDF, RDFS, URIRef
import structlog

logger = structlog.get_logger()


class ManuscriptRDFConverter(_ModelRDFConverter[Manuscript]):
    def base_triples(self) -> Iterable[_Triples]:
        pass
