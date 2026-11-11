import secrets
import bcrypt


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt (satisfies AICMS-SR-007, TC-SEC-07).
    Never stores or logs plaintext passwords.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def generate_session_token() -> str:
    """
    Generate an opaque, cryptographically secure 256-bit token (64 hex characters)
    for server-side session tracking (satisfies TC-SEC-09).
    """
    return secrets.token_hex(32)
