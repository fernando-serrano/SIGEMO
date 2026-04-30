from __future__ import annotations

import hashlib
import hmac
import os

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 120_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    raw_password = password.strip()
    if not raw_password:
        raise ValueError("La contrasena no puede estar vacia")

    salt = os.urandom(SALT_BYTES).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        bytes.fromhex(salt),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt}${digest}"


def is_password_hash(value: str) -> bool:
    return value.startswith(f"{PBKDF2_PREFIX}$")


def verify_password(password: str, stored_value: str) -> bool:
    raw_password = password.strip()
    persisted_value = stored_value.strip()

    if not raw_password or not persisted_value:
        return False

    if not is_password_hash(persisted_value):
        return hmac.compare_digest(raw_password, persisted_value)

    try:
        _, iterations_raw, salt, expected_digest = persisted_value.split("$", 3)
        iterations = int(iterations_raw)
    except ValueError:
        return False

    computed_digest = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        bytes.fromhex(salt),
        iterations,
    ).hex()
    return hmac.compare_digest(computed_digest, expected_digest)
