import logging, os
from logging.handlers import TimedRotatingFileHandler

def setup_logging(log_path="logs/scraper.jsonl", level=logging.INFO):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger = logging.getLogger("scraper")
    logger.setLevel(level)

    # Human console
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    ch.setLevel(level)

    # JSONL file (1 line/event)
    class JsonFormatter(logging.Formatter):
        import json
        def format(self, record):
            from json import dumps
            base = {
                "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                "level": record.levelname,
                "msg": record.getMessage(),
                "logger": record.name,
            }
            if record.exc_info:
                base["stack"] = self.formatException(record.exc_info)
            if hasattr(record, "kv"):
                base.update(record.kv)
            return dumps(base, ensure_ascii=False)

    fh = TimedRotatingFileHandler(log_path, when="D", interval=1, backupCount=14, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    fh.setLevel(level)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
    return logger
