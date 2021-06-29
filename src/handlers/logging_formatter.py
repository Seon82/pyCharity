import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and customize messages."""

    blue = "\x1b[1;34m"
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    record_format = "[%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: blue + record_format + reset,
        logging.INFO: grey + record_format + reset,
        logging.WARNING: yellow + record_format + reset,
        logging.ERROR: red + record_format + reset,
        logging.CRITICAL: bold_red + record_format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the provided record."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def root_logger(name, level="INFO"):
    """
    Get a logger using CustomFormatter.

    :param name: The logger's name.
    :param level: The logger's level.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    return logger
