"""Authentication endpoints (local authentication foundation)."""

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DbSession, SettingsDep
from app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse, UserResponse
from app.services.auth import AuthService, InvalidCredentialsError

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: DbSession, settings: SettingsDep) -> TokenResponse:
    """Exchange email and password for a JWT access token."""
    try:
        _, token, expires_in = await AuthService(session, settings).login(
            body.email, body.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        ) from exc
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post("/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    """Log out.

    JWTs are stateless: this endpoint does not invalidate the token
    server-side. Token revocation is planned for a later authentication
    iteration; until then tokens expire naturally.
    """
    return LogoutResponse(
        message="Logged out.",
        detail=(
            "JWTs are stateless; the current token remains valid until it "
            "expires. Server-side token revocation is planned for a later phase."
        ),
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    """Return the currently authenticated user."""
    return UserResponse.model_validate(current_user)