from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.peak_load import PeakLoadModel
from shared.dtos.peak_load import CreatePeakLoadDTO
from shared.entities.peak_load import PeakLoad

retort = ConversionRetort()

peak_load__map_from_db = retort.get_converter(PeakLoadModel, PeakLoad)
peak_load__map_to_db = retort.get_converter(PeakLoad, PeakLoadModel)
peak_load__create_mapper = retort.get_converter(
    CreatePeakLoadDTO,
    PeakLoadModel,
    recipe=[allow_unlinked_optional(P[PeakLoadModel].peak_id)],
)
