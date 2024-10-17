"""Pydantic models for Kekaumenos extraction."""

import json
from typing import Annotated

from pydantic import AnyUrl, BaseModel
from rdfproxy import SPARQLBinding
from rdfproxy import ModelBindingsMapper


# class KekaumenosSAWSModel(BaseModel):
#     saws_id: Annotated[str, SPARQLBinding("object")]
#     data: KekaumenosSAWSData


# [
#     {
#         "saws_id": <saws_id>,
#         "data": {
#             "<p>": <value>,
#             ...
#         }
#     }
# ]


x = [
    {
        "object": "http://www.ancientwisdoms.ac.uk/cts/urn:cts:greekLit:tlg3017.Syno298.sawsEng01:div1.e002",
        "p": "saws:variantOf",
        "o": "http://data.perseus.org/citations/urn:cts:greekLit:tlg0031.tlg004.perseus-eng1:19.10",
    },
    {
        "object": "http://www.ancientwisdoms.ac.uk/cts/urn:cts:greekLit:tlg3017.Syno298.sawsEng01:div1.e002",
        "p": "rdf:type",
        "o": "saws:LinguisticObject",
    },
]
