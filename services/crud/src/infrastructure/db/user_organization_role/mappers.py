from domain.users.entities import UserOrganizationRole
from domain.users.enums import RoleEnum
from shared.db.user_organization_role import UserOrganizationRoleModel


def to_model(entity: UserOrganizationRole) -> UserOrganizationRoleModel:
    return UserOrganizationRoleModel(
        user_id=entity.user_id,
        organization_id=entity.organization_id,
        role=entity.role.value,
    )


def to_entity(model: UserOrganizationRoleModel) -> UserOrganizationRole:
    return UserOrganizationRole(
        user_id=model.user_id,
        organization_id=model.organization_id,
        role=RoleEnum(model.role),
    )
