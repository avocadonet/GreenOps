from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User

from .models import UserDatabaseModel

retort = ConversionRetort(recipe=[])

user__map_from_db = retort.get_converter(UserDatabaseModel, User)

user__map_to_db = retort.get_converter(User, UserDatabaseModel)

user__create_mapper = retort.get_converter(
    CreateUserDto,
    UserDatabaseModel,
    recipe=[
        allow_unlinked_optional(P[UserDatabaseModel].user_id),
    ],
)
