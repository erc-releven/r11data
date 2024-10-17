"""Queries for Kekaumenos data extraction."""

from string import Template

_query_template_str: str = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX saws: <http://purl.org/saws/ontology#>

select ?object ?p ?o
where {
    ?object a saws:LinguisticObject ;
    saws:fallsWithin* <http://www.ancientwisdoms.ac.uk/cts/urn:cts:greekLit:tlg3017.Syno298.$source_id> ;
    <http://www.homermultitext.org/cts/rdf/hasTextContent> ?text .

  minus {?object ^saws:fallsWithin ?upper .}

  ?object ?p ?o .
}
order by ?object
"""

query_template = Template(_query_template_str)


eng_id = "sawsEng01"
grc_id = "sawsGrc01"

kekaumenos_eng_query = query_template.substitute(source_id=eng_id)
kekaumenos_grc_query = query_template.substitute(source_id=grc_id)
