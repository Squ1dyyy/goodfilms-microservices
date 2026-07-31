from fastapi import APIRouter, Depends, status

from auth.app.api.v1 import auth_events
from auth.app.service.client_info_service import get_client_info
from auth.app.api.v1.dependencies import (
    CurrentUser,
    CredentialsDep,
    RateLimitDep,
    AuthFullServiceDep,
    AuthLightServiceDep,
)
from auth.app.schemas.session import (
    SessionSchema,
    TokenResponseSchema,
    RefreshTokenSchema,
)
from auth.app.schemas.user import (
    LoginUserSchema,
    UserPublicSchema,
    RegisterUserSchema,
    UserDataSchema,
    EditPasswordSchema,
    EmailSchema,
    NewPasswordSchema,
)
from auth.core import security
from auth.core.limiter import key_by_email, key_by_ip, key_by_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterUserSchema,
    auth_service: AuthFullServiceDep,
    client_info: dict = Depends(get_client_info),
) -> TokenResponseSchema:
    user, refresh_token = await auth_service.register(
        data=data,
        client_info=client_info,
    )
    await auth_events.welcome_message(data.email)

    return TokenResponseSchema(
        access_token=security.create_access_token(
            user.id, user.role, is_verified=user.is_verified
        ),
        refresh_token=refresh_token,
        user=UserPublicSchema.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: LoginUserSchema,
    auth_service: AuthFullServiceDep,
    client_info: dict = Depends(get_client_info),
) -> TokenResponseSchema:
    user, refresh_token = await auth_service.authenticate(
        data=data,
        client_info=client_info,
    )
    return TokenResponseSchema(
        access_token=security.create_access_token(
            user.id, user.role, is_verified=user.is_verified
        ),
        refresh_token=refresh_token,
        user=UserPublicSchema.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    data: RefreshTokenSchema,
    auth_service: AuthFullServiceDep,
) -> TokenResponseSchema:
    user, access_token = await auth_service.refresh_access_token(
        refresh_token=data.refresh_token,
    )
    return TokenResponseSchema(
        access_token=access_token,
        refresh_token=data.refresh_token,
        user=UserPublicSchema.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenSchema,
    auth_service: AuthFullServiceDep,
) -> None:
    await auth_service.logout(refresh_token=data.refresh_token)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserDataSchema)
async def me(user: CurrentUser) -> UserDataSchema:
    return UserDataSchema.model_validate(user)


@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: EmailSchema,
    auth_service: AuthFullServiceDep,
    _ip_limit=RateLimitDep("5/hour", by=key_by_ip),
    _email_hour_limit=RateLimitDep("5/hour", by=key_by_email),
    _email_min_limit=RateLimitDep("1/minute", by=key_by_email),
):
    token = await auth_service.forgot_password(data.email)
    if token:
        await auth_events.forgot_password(data.email, token)


@router.get("/reset_password", status_code=status.HTTP_200_OK)
async def verify_reset_token(
    token: str,
    auth_service: AuthLightServiceDep,
):
    await auth_service.verify_token(token)
    return {"status": "success"}


@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(
    token: str,
    auth_service: AuthFullServiceDep,
    data: NewPasswordSchema,
):
    await auth_service.reset_password(token, data.new_password)
    return {"status": "success"}


@router.post("/verify_email", status_code=status.HTTP_200_OK)
async def verify_email(
    code: int,
    auth_service: AuthFullServiceDep,
    _ip_min_limit: None = RateLimitDep("5/minute", by=key_by_ip),
    _ip_hour_limit: None = RateLimitDep("10/hour", by=key_by_ip),
):
    await auth_service.verify_email(code)
    return {"status": "success"}


@router.post("/send_verification", status_code=status.HTTP_200_OK)
async def send_verification(
    user: CurrentUser,
    auth_service: AuthLightServiceDep,
    _user_min_limit: None = RateLimitDep("1/minute", by=key_by_user_id),
    _user_day_limit: None = RateLimitDep("3/day", by=key_by_user_id),
):
    code = await auth_service.send_verification(user.id)
    await auth_events.send_verification(user.email, code)
    return {"status": "success"}


@router.patch(
    "/password",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponseSchema,
)
async def change_password(
    data: EditPasswordSchema,
    user: CurrentUser,
    auth_service: AuthFullServiceDep,
    client_info: dict = Depends(get_client_info),
) -> TokenResponseSchema:
    user, refresh_token = await auth_service.change_password(user, data, client_info)
    return TokenResponseSchema(
        access_token=security.create_access_token(
            user.id, user.role, is_verified=user.is_verified
        ),
        refresh_token=refresh_token,
        user=UserPublicSchema.model_validate(user),
    )


@router.get(
    "/sessions",
    status_code=status.HTTP_200_OK,
    response_model=list[SessionSchema],
)
async def sessions(
    data: CurrentUser,
    auth_service: AuthFullServiceDep,
) -> list[SessionSchema]:
    return await auth_service.get_sessions(data)


@router.delete("/sessions/all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_sessions(
    auth_service: AuthFullServiceDep,
    credentials: CredentialsDep,
) -> None:
    await auth_service.delete_sessions(credentials.credentials)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    auth_service: AuthFullServiceDep,
    data: CurrentUser,
) -> None:
    await auth_service.delete_session_by_id(session_id, data.id)
