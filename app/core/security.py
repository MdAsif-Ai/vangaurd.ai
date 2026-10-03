"""Security primitives: password hashing and JWT creation/verification."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password (Argon2 when available, otherwise bcrypt)."""
    return _password_hasher.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return _password_hasher.verify(plain_password, password_hash)


def create_access_token(
    *,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
    role: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 60,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "org": str(organization_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, *, secret_key: str, algorithm: str = "HS256") -> dict[str, Any]:
    """Decode and verify a JWT.

    Raises jwt.PyJWTError subclasses (e.g. ExpiredSignatureError) when the
    token is invalid or expired.
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])
