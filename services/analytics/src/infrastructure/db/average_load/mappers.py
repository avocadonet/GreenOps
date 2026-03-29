from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.average_load import AverageLoadModel
from shared.dtos.average_load import CreateAverageLoadDTO
from shared.entities.average_load import AverageLoad

retort = ConversionRetort()

average_load__map_from_db = retort.get_converter(AverageLoadModel, AverageLoad)
average_load__create_mapper = retort.get_converter(
    CreateAverageLoadDTO,
    AverageLoadModel,
    recipe=[allow_unlinked_optional(P[AverageLoadModel].avg_load_id)],
)
