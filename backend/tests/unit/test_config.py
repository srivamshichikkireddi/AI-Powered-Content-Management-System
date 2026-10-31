from backend.app.core.config import settings
from backend.app.core.logging import StructuredJsonFormatter, correlation_id_ctx
import json
import logging


def test_settings_defaults():
    """Verify application configuration defaults."""
    assert settings.PROJECT_NAME == "AI-Powered Content Management System (AICMS)"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.MAX_FAILED_LOGIN_ATTEMPTS == 5
    assert settings.MAX_UPLOAD_SIZE_BYTES == 20 * 1024 * 1024
    assert len(settings.cors_origins_list) >= 1


def test_structured_logging_redacts_sensitive_keys():
    """Verify AICMS-NF-006: Structured logs redact secrets, tokens, passwords."""
    formatter = StructuredJsonFormatter()
    token = correlation_id_ctx.set("test-corr-id-12345")
    try:
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="User login attempt",
            args=(),
            exc_info=None,
        )
        record.extra = {
            "username": "alice",
            "password": "SuperSecretPassword123",
            "token": "eyJhbGciOi...",
            "safe_meta": "active",
        }
        output = formatter.format(record)
        parsed = json.loads(output)

        assert parsed["correlation_id"] == "test-corr-id-12345"
        assert parsed["message"] == "User login attempt"
        assert parsed["extra"]["username"] == "alice"
        assert parsed["extra"]["password"] == "[REDACTED]"
        assert parsed["extra"]["token"] == "[REDACTED]"
        assert parsed["extra"]["safe_meta"] == "active"
    finally:
        correlation_id_ctx.reset(token)
