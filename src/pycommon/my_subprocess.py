""" Wrap some subprocess functions to add a timer """
from datetime import datetime
from subprocess import DEVNULL, PIPE, CompletedProcess
from subprocess import run as real_run

__all__ = ["run", "DEVNULL", "PIPE"]


# noinspection PyMissingConstructor
class CompletedProcessExt(CompletedProcess):  # pylint: disable=too-few-public-methods
    """Override the CompletedProcess class to add elapsed_time attribute. we could have
    just added the elapsed_time attribute to the CompletedProcess class, but that would
    mean pylint errors everywhere we access it."""

    def __init__(
        self, elapsed_time: str, parent: CompletedProcess
    ):  # pylint: disable=super-init-not-called
        # We DELIBERATELY do not call super().__init__() here -
        # we get the data from "parent" explicitly
        self.elapsed_time = elapsed_time
        self.__dict__.update(parent.__dict__)

    def __repr__(self):
        args = super().__repr__()

        return f"{args[:-1]},elapsed_time='{self.elapsed_time}')"


def run(*args, **kwargs):
    """Wrap subprocess.run() with timer"""
    start_time = datetime.now()
    result = real_run(*args, **kwargs)  # pylint: disable=subprocess-run-check
    elapsed_time = datetime.now() - start_time
    hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return CompletedProcessExt(
        elapsed_time=f"{hours:02}:{minutes:02}:{int(seconds):02}", parent=result
    )
    # return result
