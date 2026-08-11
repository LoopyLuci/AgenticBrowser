import json
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "file": record.filename,
        }
        if hasattr(record, "trace_id"):
            base["trace_id"] = record.trace_id
        extra = {k: v for k, v in record.__dict__.items() if k not in logging.LogRecord("", 0, "", 0, "", (), None).__dict__ and not k.startswith("_")}
        base.update(extra)
        return json.dumps(base)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(os.getenv("AGENTIC_LOG_LEVEL", "INFO"))
    fmt = JsonFormatter()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(fmt)
    logger.addHandler(stdout_handler)
    log_path = os.getenv("AGENTIC_LOG_FILE", "logs/app.jsonl")
    os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else ".", exist_ok=True)
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
