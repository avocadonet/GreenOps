from domain.users.entities import User, UserOrganizationRole

from application.users.dtos import DeleteUserRoleDto, UpdateUserDto

from .schemas import (
    CreateRoleRequest,
    UpdateRoleRequest,
    UpdateUserRequest,
    UserOrganizationRoleResponse,
    UserResponse,
)


def user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        fullname=user.fullname,
        is_active=user.is_active,
        telegram_id=user.telegram_id,
        created_at=user.created_at,
        role=user.role,
    )


def update_request_to_dto(request: UpdateUserRequest, user_id: int) -> UpdateUserDto:
    return UpdateUserDto(
        user_id=user_id,
        fullname=request.fullname,
        telegram_id=request.telegram_id,
        send_to_type=request.send_to_type,
    )


def role_to_response(role: UserOrganizationRole) -> UserOrganizationRoleResponse:
    return UserOrganizationRoleResponse(
        user_id=role.user_id,
        organization_id=role.organization_id,
        role=role.role,
    )


def create_role_request_to_entity(request: CreateRoleRequest) -> UserOrganizationRole:
    return UserOrganizationRole(
        user_id=request.user_id,
        organization_id=request.organization_id,
        role=request.role,
    )


def update_role_request_to_entity(
    request: UpdateRoleRequest, user_id: int, organization_id: int
) -> UserOrganizationRole:
    return UserOrganizationRole(
        user_id=user_id,
        organization_id=organization_id,
        role=request.role,
    )


def delete_role_to_dto(user_id: int, organization_id: int) -> DeleteUserRoleDto:
    return DeleteUserRoleDto(user_id=user_id, organization_id=organization_id)
