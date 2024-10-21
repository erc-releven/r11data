"""Pydantic models for Kekaumenos extraction."""

import json
from typing import Annotated, Union

from pydantic import AnyUrl, BaseModel, Field
from rdflib import Namespace

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dc = Namespace("http://purl.org/dc/terms/")
saws = Namespace("http://purl.org/saws/ontology#")
cts = Namespace("http://www.homermultitext.org/cts/rdf/")


class KekaumenosSAWSDataField(BaseModel):
    is_variant_of: str | None = Field(validation_alias=saws.isVariantOf, default=None)
    a: str = Field(validation_alias=rdf.type)
    falls_within: str = Field(validation_alias=saws.fallsWithin)
    is_close_translation_of: str | None = Field(
        validation_alias=saws.isCloseTranslationOf, default=None
    )
    has_text_content: str = Field(validation_alias=cts.hasTextContent)
    provenance: str | None = Field(validation_alias=dc.provenance, default=None)
    rdf_schema_label: str = Field(validation_alias=rdfs.label)


class KekaumenosSAWSModel(BaseModel):
    node_id: str
    data: KekaumenosSAWSDataField
