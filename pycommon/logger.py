""" Setup logging:
    - Log file rotates every midnight by default
    - Lines are split at 88 with subsequent indent characters
    - Log level is set to INFO
    - Console logger setup if we are on a tty
    - Continuation lines are also prefixed
    - Newlines caused by linefeeds are also prefixed
"""
import logging
import os
import textwrap
from logging.handlers import TimedRotatingFileHandler

from pycommon import config

# __all__ = ["get_logger"]


class NewLineFormatter(logging.Formatter):
    """Override the default formatter to:
    - Add the line prefix each time a '\n' is encountered
    - Split lines longer than max_width
    - Indent lines after the first line by indent characters
    """

    def __init__(self, fmt, date_format=None):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, fmt, date_format)

    def format(self, record):
        """Override format function"""
        msg = logging.Formatter.format(self, record)

        if record.message != "":
            parts = msg.split(record.message)  # Gets the line prefix so we can reuse it later

            # Handle explicit new-lines (textwrap will otherwise just remove them)
            s_arr = msg.split("\n")
            for sub, this_line in enumerate(s_arr):
                if sub == 0:
                    # We do this so that textwrap has consistent size on each line
                    this_line = this_line[len(parts[0]) :]
                else:
                    this_line = " " * config.common.log_indent + this_line
                wrapped_lines = textwrap.wrap(
                    this_line,
                    width=config.common.log_max_width,
                    subsequent_indent=" " * config.common.log_indent,
                )
                s_arr[sub] = "\n".join(wrapped_lines)
            # Put everything back together
            msg = "\n".join(s_arr)
            prefix = parts[0][:-1]
            prefix += "+"
            msg = parts[0] + msg
            msg = msg.replace("\n", "\n" + prefix)

        return msg


# noinspection SpellCheckingInspection
def get_logger(
    file_name: str,
    name: str,
    backup_count: int = 7,
    when: str = "midnight",
    interval: int = 1,
) -> logging.Logger:
    """Return a logger with a given name and level."""
    os.makedirs(config.common.log_directory, exist_ok=True)
    log_name = os.path.join(config.common.log_directory, file_name)
    file_handler = TimedRotatingFileHandler(
        log_name, when=when, interval=interval, backupCount=backup_count, utc=True
    )
    formatter = NewLineFormatter(
        "%(asctime)s %(levelname)s:%(name)s %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    file_handler.setLevel(config.common.log_level)

    file_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(config.common.log_level)
    # And a screen handler if we are interactive (PyCharm doesn't show as a tty)
    if config.common.isatty:
        console_formatter = NewLineFormatter("%(name)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        console_handler.setLevel(config.common.log_level)
        logger.addHandler(console_handler)
    return logger
