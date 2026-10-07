"""Password hashing and user auth helpers for Campus Customs.

Passwords are never stored in plain text. We store a salted PBKDF2-HMAC-SHA256
hash in the format:  pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>

- Each password gets its own random 16-byte salt, so identical passwords hash
  differently and precomputed ("rainbow table") attacks don't apply.
- PBKDF2 is deliberately slow (many iterations), which makes brute-force guessing
  expensive.
- Verification uses a constant-time compare to avoid timing attacks.
"""

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 390_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        # Any stored value that isn't in our format (e.g. legacy seed rows) fails safely.
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
    return hmac.compare_digest(digest, expected)
