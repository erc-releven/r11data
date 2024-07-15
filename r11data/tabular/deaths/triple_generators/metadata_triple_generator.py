"""Metadata triple generator from r11cli."""

from collections.abc import Iterator
from collections.abc import Callable
import datetime

from lodkit import mkuri_factory, ttl
from lodkit.types import _Triple
from r11data.tabular.deaths.utils.namespaces import crm, crmdig
from r11data.tabular.deaths.utils.utils import get_system_information
from rdflib import Literal, URIRef
from rdflib.namespace import Namespace, RDF, XSD


mkuri = mkuri_factory(Namespace("https://r11.eu/ns/star/"))


def _generate_nodes_metadata() -> Callable[..., Iterator[_Triple]]:
    """Generate metadata triples for a node."""

    r11tab = "https://github.com/erc-releven/" "DataModelSchemas/tree/main/r11tab"

    json_type = URIRef(
        "https://vocabs.sshopencloud.eu/browse/"
        "media-type/en/page/applicationslashjson"
    )

    datetime_literal = Literal(
        datetime.datetime.now().isoformat(), datatype=XSD.dateTime
    )

    def _wrapper(*nodes: URIRef):
        yield from ttl(
            mkuri("metadata d10"),
            (RDF.type, crmdig.D10_Software_Execution),
            (crmdig.L11_had_output, nodes),
            (
                crm["P4_has_time-span"],
                ttl(
                    mkuri("E52 URI"),
                    (RDF.type, crm["E52_Time-Span"]),
                    (crm.P82_begin_of_the_begin, datetime_literal),
                ),
            ),
            (
                crmdig.L23_used_software_or_firmware,
                ttl(
                    mkuri("metadata d14"),
                    (RDF.type, crmdig.D14_Software),
                    (
                        crm.P1_is_identified_by,
                        ttl(
                            mkuri("metadata e42"),
                            (RDF.type, crm.E42_Identifier),
                            (crm.P190_has_symbolic_value, Literal(r11tab)),
                        ),
                    ),
                ),
            ),
            (
                crmdig.L12_happened_on_device,
                ttl(
                    mkuri("metadata d8"),
                    (RDF.type, crmdig.D8_Digital_Device),
                    (
                        crm.P129i_is_subject_of,
                        ttl(
                            mkuri("metadata e73"),
                            (RDF.type, crm.E73_Information_Object),
                            (crm.P2_has_type, json_type),
                            (
                                crm.P190_has_symbolic_content,
                                Literal(get_system_information()),
                            ),
                        ),
                    ),
                ),
            ),
        )

    return _wrapper
