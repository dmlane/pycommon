""" Test my_subprocess
    -
"""
import re

from pycommon.my_subprocess import run


def test_run_ok():
    """Test that timer is working. Pretty meaningless, but it also tests that my version of
    subprocess behaves correctly."""
    result = run(["true"])
    assert result.returncode == 0


def test_run_fail():
    """Test that timer is working. Pretty meaningless, but it also tests that my version of
    subprocess behaves correctly."""
    result = run(["false"])
    assert result.returncode != 0


def test_elapsed_time_set():
    """Test elapsed_time is set correctly"""
    result = run(["true"])
    assert re.match(r"^\d\d:\d\d:\d\d$", result.elapsed_time)
