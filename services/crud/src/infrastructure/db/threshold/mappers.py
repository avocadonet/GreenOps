from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.threshold import ThresholdModel
from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold

retort = ConversionRetort()

threshold__map_from_db = retort.get_converter(ThresholdModel, Threshold)
threshold__map_to_db = retort.get_converter(Threshold, ThresholdModel)
threshold__create_mapper = retort.get_converter(
    CreateThresholdDTO,
    ThresholdModel,
    recipe=[allow_unlinked_optional(P[ThresholdModel].threshold_id)],
)
