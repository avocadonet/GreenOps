from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor

from .schemas import CreateSensorRequest, SensorResponse


def create_request_to_dto(request: CreateSensorRequest) -> CreateSensorDTO:
    return CreateSensorDTO(
        serial_number=request.serial_number,
        model=request.model,
        calibration_date=request.calibration_date,
        sensor_type=request.sensor_type,
        building_id=request.building_id,
        unit_id=request.unit_id,
    )


def entity_to_response(entity: Sensor) -> SensorResponse:
    return SensorResponse(
        sensor_id=entity.sensor_id,
        serial_number=entity.serial_number,
        model=entity.model,
        calibration_date=entity.calibration_date,
        sensor_type=entity.sensor_type,
        building_id=entity.building_id,
        unit_id=entity.unit_id,
    )
