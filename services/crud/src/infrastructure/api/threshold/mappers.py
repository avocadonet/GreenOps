from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold

from .schemas import CreateThresholdRequest, ThresholdResponse


def create_request_to_dto(request: CreateThresholdRequest) -> CreateThresholdDTO:
    return CreateThresholdDTO(
        sensor_id=request.sensor_id,
        limit_value=request.limit_value,
        threshold_type=request.threshold_type,
        tariff_zone=request.tariff_zone,
    )


def entity_to_response(entity: Threshold) -> ThresholdResponse:
    return ThresholdResponse(
        threshold_id=entity.threshold_id,
        sensor_id=entity.sensor_id,
        limit_value=entity.limit_value,
        threshold_type=entity.threshold_type,
        tariff_zone=entity.tariff_zone,
    )
