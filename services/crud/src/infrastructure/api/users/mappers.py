from uuid import UUID

from adaptix import P
from adaptix.conversion import ConversionRetort, link_function
from domain.auth.dtos import UpdateUserDto
from domain.auth.entities import User

from infrastructure.api.users.dtos import UpdateUserModelDto, UserModel

retort = ConversionRetort(recipe=[])

user__map_to_pydantic = retort.get_converter(User, UserModel)


@retort.impl_converter(
    recipe=[
        link_function(
            lambda dto, user_id: user_id,
            P[UpdateUserDto].user_id,
        )
    ]
)
def user__map_update_dto(dto: UpdateUserModelDto, user_id: UUID) -> UpdateUserDto: ...  # noqa
