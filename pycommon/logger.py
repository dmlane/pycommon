""" Setup logging"""
import logging
import os
import sys
import textwrap
from logging.handlers import TimedRotatingFileHandler

import appdirs
from settings import settings

__all__ = ["get_logger"]


class NewLineFormatter(logging.Formatter):
    """Override the default formatter to:
    - Add the line prefix each time a '\n' is encountered
    - Split lines longer than max_width
    - Indent lines after the first line by indent characters
    """

    def __init__(self, fmt, date_format=None, indent: int = 4, max_width: int = 88):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, fmt, date_format)
        self.dml_indent = indent
        self.dml_max_width = max_width

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
                    this_line = " " * self.dml_indent + this_line
                wrapped_lines = textwrap.wrap(
                    this_line,
                    width=self.dml_max_width,
                    subsequent_indent=" " * self.dml_indent,
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
# pylint: disable=too-many-arguments
def get_logger(
    file_name: str,
    name: str,
    log_level: str = "INFO",
    indent: int = 4,
    max_width: int = 88,
    backup_count: int = 7,
    when: str = "midnight",
    interval: int = 1,
    app_name: str = "net.dmlane",
    author: str = "dave",
    # stdout: bool = True,
) -> logging.Logger:
    # pylint: disable=too-many-locals
    """Return a logger with a given name and level."""
    log_directory = appdirs.user_log_dir(app_name, author)
    os.makedirs(log_directory, exist_ok=True)
    log_name = log_directory + "/" + file_name
    file_handler = TimedRotatingFileHandler(
        log_name, when=when, interval=interval, backupCount=backup_count, utc=True
    )
    formatter = NewLineFormatter(
        "%(asctime)s %(levelname)s:%(name)s %(message)s",
        "%Y-%m-%d %H:%M:%S",
        indent=indent,
        max_width=max_width,
    )
    file_handler.setLevel(log_level)

    file_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    logger.setLevel(log_level)
    # And a screen handler if we are interactive (PyCharm doesn't show as a tty)
    if sys.stdout.isatty() or "PYCHARM_HOSTED" in os.environ:
        console_formatter = NewLineFormatter("%(name)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    return logger
