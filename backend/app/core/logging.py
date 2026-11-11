import contextvars
import json
import logging
import sys
import uuid
from typing import Any, Dict

correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


def get_correlation_id() -> str:
    cid = correlation_id_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid


class StructuredJsonFormatter(logging.Formatter):
    """
    Structured JSON formatter ensuring compliance with AICMS-NF-006:
    Structured logs, correlation IDs, no raw document text or sensitive secrets.
    """

    SENSITIVE_KEYS = {
        "password",
        "secret",
        "token",
        "authorization",
        "access_token",
        "raw_text",
        "content",
        "embedding",
    }

    def _sanitize(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if k.lower() in self.SENSITIVE_KEYS else self._sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self._sanitize(item) for item in obj]
        return obj

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get() or "N/A",
        }

        if hasattr(record, "extra") and isinstance(record.extra, dict):  # type: ignore
            log_entry["extra"] = self._sanitize(record.extra)  # type: ignore

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())

    root = logging.getLogger()
    root.setLevel(level.upper())
    root.handlers = [handler]

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
