from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.metric import MetricModel
from shared.dtos.metric import CreateMetricDTO
from shared.entities.metric import Metric

retort = ConversionRetort()

metric__map_from_db = retort.get_converter(MetricModel, Metric)
metric__map_to_db = retort.get_converter(Metric, MetricModel)
metric__create_mapper = retort.get_converter(
    CreateMetricDTO,
    MetricModel,
    recipe=[allow_unlinked_optional(P[MetricModel].metric_id)],
)
