"""SPARQL construct templates for starleg generation."""

from string import Template

from r11data.starlegs.utils._types import CRMTemplateMap

_base_sparql_template: str = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX star: <https://r11.eu/ns/star/>
PREFIX sdhss: <https://r11.eu/ns/prosopography/>

construct {
    ?o crm:P14_carried_out_by ?agent .
    ?o crm:P17_was_motivated_by ?source .
}
where {
    ?e13_initial a star:$target_class ;
    	$common_connector ?common .

    optional {?e13_initial crm:P14_carried_out_by ?agent}
    optional {?e13_initial crm:P17_was_motivated_by ?source}

    ?common ^crm:P140_assigned_attribute_to ?o .
    filter (?o != ?e13_initial)

    minus {?o crm:P14_carried_out_by ?agent}
    minus {?o crm:P17_was_motivated_by ?source}
}
"""


_p140_sparql_template: str = Template(_base_sparql_template).safe_substitute(
    common_connector="crm:P140_assigned_attribute_to"
)
_p141_sparql_template: str = Template(_base_sparql_template).safe_substitute(
    common_connector="crm:P141_assigned"
)

_p140_template: Template = Template(_p140_sparql_template)
_p141_template: Template = Template(_p141_sparql_template)

p140_template_map: CRMTemplateMap = CRMTemplateMap(
    sparql_construct_template=_p140_template,
    crm_classes=[
        "E13_sdhss_P13",
        "E13_sdhss_P26",
        "E13_sdhss_P36",
        "E13_crm_P41",
    ],
)
p141_template_map: CRMTemplateMap = CRMTemplateMap(
    sparql_construct_template=_p141_template, crm_classes=["E13_sdhss_P38"]
)
