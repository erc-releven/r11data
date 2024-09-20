"""Custom types for starlegs functionality."""

from dataclasses import dataclass
from string import Template


@dataclass
class CRMTemplateMap:
    """Simple dataclass for associating a construct template with applicable CRM classes."""

    sparql_construct_template: Template
    crm_classes: list[str]
