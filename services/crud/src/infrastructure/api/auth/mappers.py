from adaptix import P
from adaptix.conversion import ConversionRetort, link_function
from application.auth.dtos import AuthenticateUserDto, RegisterUserDto

from infrastructure.api.auth.schemas import AuthenticateUserModelDto, CreateUserModelDto

retort = ConversionRetort(recipe=[])

map_authenticate_dto = retort.get_converter(
    AuthenticateUserModelDto,
    AuthenticateUserDto,
    recipe=[
        link_function(
            lambda user: user.email,
            P[AuthenticateUserDto].email,
        ),
    ],
)

map_create_dto = retort.get_converter(
    CreateUserModelDto,
    RegisterUserDto,
    recipe=[
        link_function(
            lambda user: user.email,
            P[RegisterUserDto].email,
        ),
        link_function(
            lambda user: user.org_id,
            P[RegisterUserDto].org_id,
        ),
        link_function(
            lambda user: user.role,
            P[RegisterUserDto].role,
        ),
    ],
)
