"""Security primitive tests: password hashing and JWT."""

import uuid

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

SECRET = "unit-test-secret"


def test_password_hash_roundtrip() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_create_and_decode_access_token() -> None:
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    token = create_access_token(
        user_id=user_id,
        organization_id=organization_id,
        role="admin",
        secret_key=SECRET,
    )
    payload = decode_access_token(token, secret_key=SECRET)
    assert payload["sub"] == str(user_id)
    assert payload["org"] == str(organization_id)
    assert payload["role"] == "admin"


def test_expired_token_is_rejected() -> None:
    token = create_access_token(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="user",
        secret_key=SECRET,
        expires_minutes=-1,
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token, secret_key=SECRET)


def test_token_with_wrong_secret_is_rejected() -> None:
    token = create_access_token(
        user_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
        role="user",
        secret_key=SECRET,
    )
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token, secret_key="another-secret")