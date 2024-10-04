"""Testing utils for starlegs construction."""

from rdflib import Graph


def starlegs_missing_p(graph: Graph) -> bool:
    """Check if starlegs are missing in a Graph."""

    missing_starlegs_p_query: str = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
    PREFIX star: <https://r11.eu/ns/star/>
    PREFIX sdhss: <https://r11.eu/ns/prosopography/>

    ask
    where {
    ?e13_initial a ?target_class ;
    	crm:P140_assigned_attribute_to | crm:P141_assigned ?common .

    optional {?e13_initial crm:P14_carried_out_by ?agent}
    optional {?e13_initial crm:P17_was_motivated_by ?source}

    ?common ^crm:P140_assigned_attribute_to ?o .
    filter (?o != ?e13_initial)

    minus {?o crm:P14_carried_out_by ?agent}
    minus {?o crm:P17_was_motivated_by ?source}
    }
    """

    answer = graph.query(missing_starlegs_p_query)
    return answer.askAnswer
