"""Authentication service: login with an audit trail."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import create_access_token, verify_password
from app.db.models import User
from app.db.repositories import AuditLogRepository, UserRepository


class InvalidCredentialsError(Exception):
    """Raised when the email/password pair does not match an active user."""


class AuthService:
    """Business logic for local authentication."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._audit = AuditLogRepository(session)

    async def login(self, email: str, password: str) -> tuple[User, str, int]:
        """Authenticate a user and issue a JWT access token.

        Returns (user, token, lifetime in seconds).
        """
        normalized_email = email.lower()
        user = await self._users.get_by_email(normalized_email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            await self._audit.log(
                organization_id=user.organization_id if user else None,
                user_id=user.id if user else None,
                action="auth.login_failed",
                meta={"email": normalized_email},
            )
            await self._session.commit()
            raise InvalidCredentialsError("Incorrect email or password.")

        token = create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
            role=user.role.value,
            secret_key=self._settings.jwt_secret_key.get_secret_value(),
            algorithm=self._settings.jwt_algorithm,
            expires_minutes=self._settings.access_token_expire_minutes,
        )
        await self._audit.log(
            organization_id=user.organization_id,
            user_id=user.id,
            action="auth.login",
            resource_type="user",
            resource_id=str(user.id),
        )
        await self._session.commit()
        return user, token, self._settings.access_token_expire_minutes * 60
