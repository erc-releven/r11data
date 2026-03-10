from collections.abc import Iterable, Iterator

from lodkit import _Triple as Triple
from r11data.tabular.models import LocationSheetModel
from r11data.tabular.utils.rdf_utils import TripleChain


class LocationsTripleGenerator[TModel: LocationSheetModel](Iterable[Triple]):
    def __init__(self, model: TModel) -> None:
        self.model = model

    def __iter__(self) -> Iterator[Triple]:
        return TripleChain()
