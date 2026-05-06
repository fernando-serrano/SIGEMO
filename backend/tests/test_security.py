from app.utils.security import hash_password, is_password_hash, verify_password
from app.utils.auth_tokens import TokenError, create_access_token, decode_access_token


def test_hash_password_uses_pbkdf2_and_verifies_plain_password():
    stored_password = hash_password("secret-value")

    assert is_password_hash(stored_password)
    assert verify_password("secret-value", stored_password)
    assert not verify_password("wrong-value", stored_password)


def test_verify_password_keeps_legacy_plaintext_compatibility():
    assert verify_password("legacy", "legacy")
    assert not verify_password("legacy", "other")


def test_access_token_roundtrip():
    token = create_access_token(
        subject="user-1",
        username="fserrano",
        role="ADMIN",
        secret_key="test-secret",
        expires_in_seconds=120,
    )

    payload = decode_access_token(token, secret_key="test-secret")

    assert payload["sub"] == "user-1"
    assert payload["username"] == "fserrano"
    assert payload["role"] == "ADMIN"


def test_access_token_rejects_wrong_secret():
    token = create_access_token(
        subject="user-1",
        username="fserrano",
        secret_key="test-secret",
        expires_in_seconds=120,
    )

    try:
        decode_access_token(token, secret_key="other-secret")
    except TokenError as error:
        assert "Firma invalida" in str(error)
    else:
        raise AssertionError("Expected TokenError for invalid signature")
