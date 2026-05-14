from application.auth.dtos import AuthenticateUserDto, RegisterUserDto
from application.auth.services import AuthService
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from infrastructure.api.schemas import ErrorModel

from .schemas import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse

router = APIRouter(prefix="/auth", route_class=DishkaRoute, tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorModel}},
)
async def login(
    body: LoginRequest,
    auth: FromDishka[AuthService],
):
    user, tokens = await auth.login(
        AuthenticateUserDto(email=body.email, password=body.password)
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user_id=user.id,
        email=user.email,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    responses={409: {"model": ErrorModel}},
)
async def register(
    body: RegisterRequest,
    auth: FromDishka[AuthService],
):
    user = await auth.register(
        RegisterUserDto(
            email=body.email, password=body.password, fullname=body.fullname
        )
    )
    return RegisterResponse(
        message="User registered. Activate your account to log in.",
        user_id=user.id,
        email=user.email,
    )
