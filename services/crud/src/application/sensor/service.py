from datetime import date
from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from domain.sensor.exceptions import SensorAttachmentException
from domain.sensor.repository import SensorRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from shared.dtos.sensor import CreateSensorDTO
from shared.entities.sensor import Sensor
from shared.enums import SensorType


class SensorService:
    def __init__(
        self,
        repository: SensorRepository,
        tx: TransactionsGateway,
        role_getter: RoleGetter,
    ) -> None:
        self._repository = repository
        self._tx = tx
        self._role_getter = role_getter

    def _check(self, user: User, *perms: PermissionsEnum) -> None:
        PermissionBuilder().providers(UserPermissionProvider(user)).add(*perms).apply()

    async def _check_org(self, user: User, organization_id: int, *perms: PermissionsEnum) -> None:
        org_role = await self._role_getter(user, organization_id)
        PermissionBuilder().providers(OrgPermissionProvider(org_role)).add(*perms).apply()

    async def list_all(self, user: User, building_id: UUID | None, organization_id: int | None, page: int, page_size: int) -> list[Sensor]:
        if organization_id is not None:
            await self._check_org(user, organization_id, PermissionsEnum.CAN_READ_SENSOR)
        else:
            self._check(user, PermissionsEnum.CAN_READ_SENSOR)
        if building_id is not None:
            return await self._repository.list_by_building(building_id, page, page_size)
        return await self._repository.list_all(organization_id, page, page_size)

    async def create(self, user: User, dto: CreateSensorDTO) -> Sensor:
        if dto.organization_id is not None:
            await self._check_org(user, dto.organization_id, PermissionsEnum.CAN_CREATE_SENSOR)
        else:
            self._check(user, PermissionsEnum.CAN_CREATE_SENSOR)
        self._validate_attachment(dto.sensor_type, dto.building_id, dto.unit_id)
        return await self._repository.create(dto)

    async def read(self, user: User, sensor_id: UUID) -> Sensor:
        sensor = await self._repository.read(sensor_id)
        if sensor.organization_id is not None:
            await self._check_org(user, sensor.organization_id, PermissionsEnum.CAN_READ_SENSOR)
        else:
            self._check(user, PermissionsEnum.CAN_READ_SENSOR)
        return sensor

    async def update(self, user: User, sensor_id: UUID, serial_number: str, model: str, calibration_date: date) -> Sensor:
        async with self._tx:
            sensor = await self._repository.read(sensor_id)
            if sensor.organization_id is not None:
                await self._check_org(user, sensor.organization_id, PermissionsEnum.CAN_UPDATE_SENSOR)
            else:
                self._check(user, PermissionsEnum.CAN_UPDATE_SENSOR)
            sensor.serial_number = serial_number
            sensor.model = model
            sensor.calibration_date = calibration_date
            return await self._repository.update(sensor)

    async def delete(self, user: User, sensor_id: UUID) -> Sensor:
        async with self._tx:
            sensor = await self._repository.read(sensor_id)
            if sensor.organization_id is not None:
                await self._check_org(user, sensor.organization_id, PermissionsEnum.CAN_DELETE_SENSOR)
            else:
                self._check(user, PermissionsEnum.CAN_DELETE_SENSOR)
            return await self._repository.delete(sensor)

    @staticmethod
    def _validate_attachment(
        sensor_type: SensorType,
        building_id: UUID | None,
        unit_id: UUID | None,
    ) -> None:
        if building_id is not None and unit_id is not None:
            raise SensorAttachmentException(
                "Sensor cannot be attached to both a building and a unit"
            )
        if sensor_type == SensorType.COMMON and building_id is None:
            raise SensorAttachmentException("COMMON sensor requires building_id")
        if sensor_type == SensorType.INDIVIDUAL and unit_id is None:
            raise SensorAttachmentException("INDIVIDUAL sensor requires unit_id")
