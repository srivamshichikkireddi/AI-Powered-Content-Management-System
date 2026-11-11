from backend.app.core.security import get_password_hash, verify_password, generate_session_token


def test_password_hashing_bcrypt_tc_sec_07():
    """
    TC-SEC-07: Verify password hashing with bcrypt.
    - Password is never stored in plain text.
    - Resulting hash starts with standard bcrypt identifier ($2b$).
    - Verifies matching passwords and rejects incorrect passwords.
    """
    raw_pass = "SecurePass#2026!"
    hashed = get_password_hash(raw_pass)

    assert hashed != raw_pass
    assert hashed.startswith("$2b$")
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


def test_session_token_generation_entropy():
    """Verify session token is 64 hex characters (256 bits of cryptographic entropy)."""
    t1 = generate_session_token()
    t2 = generate_session_token()
    assert len(t1) == 64
    assert len(t2) == 64
    assert t1 != t2
