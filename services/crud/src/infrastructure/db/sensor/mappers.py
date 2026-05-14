from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.sensor import SensorModel
from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor

retort = ConversionRetort()

sensor__map_from_db = retort.get_converter(SensorModel, Sensor)
sensor__map_to_db = retort.get_converter(Sensor, SensorModel)
sensor__create_mapper = retort.get_converter(
    CreateSensorDTO,
    SensorModel,
    recipe=[allow_unlinked_optional(P[SensorModel].sensor_id)],
)
