import json
import logging
import os
import sys


class _ConfigurationState:
    configured = False


_state = _ConfigurationState()


def _json_formatter(record: logging.LogRecord) -> str:
    payload = {
        "level": record.levelname,
        "name": record.name,
        "time": record.created,  # epoch seconds
        "message": record.getMessage(),
        "module": record.module,
        "func": record.funcName,
        "line": record.lineno,
    }
    if record.exc_info:
        payload["exc_info"] = logging.Formatter().formatException(record.exc_info)
    return json.dumps(payload, ensure_ascii=False)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return _json_formatter(record)


def configure_logging() -> None:
    """
    Configure root logger exactly once.
    ENV:
      LOG_LEVEL=DEBUG|INFO|WARNING|ERROR|CRITICAL (default INFO)
      LOG_FORMAT=json|plain (default plain)
      LOG_FILE=/path/to/file.log (optional; if set, also logs to file)
    """
    if _state.configured:
        return

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "plain").lower()
    log_file = os.getenv("LOG_FILE")

    root = logging.getLogger()
    root.setLevel(level)

    # Remove any pre-existing handlers (e.g., when rerun in notebooks)
    for h in list(root.handlers):
        root.removeHandler(h)

    # Console handler
    ch = logging.StreamHandler(stream=sys.stdout)
    if fmt == "json":
        ch.setFormatter(JsonFormatter())
    else:
        ch.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
    root.addHandler(ch)

    # Optional file handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(
            JsonFormatter()
            if fmt == "json"
            else logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        root.addHandler(fh)

    _state.configured = True
