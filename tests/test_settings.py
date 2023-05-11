""" Test my_settings module"""
import logging
import os
import shutil
from importlib import resources

import appdirs
import pytest
from my_settings import MySettings


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Runs before and after each test"""
    package_name = "pycommon"
    config_file = appdirs.user_config_dir("dmlane", "dave") + "/settings.toml"
    config_backup = str(resources.files(package_name)) + "/data/settings_backup.toml"
    if os.path.exists(config_file):
        shutil.move(config_file, config_backup)

    yield
    if os.path.exists(config_backup):
        shutil.move(config_backup, config_file)


def test_basic_usage():
    """Test basic usage with package config file only"""
    config = MySettings()
    assert config.logger.log_indent == 4


def test_change_config_file(monkeypatch, resource_path_root):
    """Test changing config file on the command line
    - uses tests/testresources/settings1.toml"""
    test_config_file = os.path.join(resource_path_root, "settings1.toml")
    monkeypatch.setattr(
        "sys.argv",
        [
            "my_settings.py",
            "--config-file",
            test_config_file,
        ],
    )
    config = MySettings()
    assert config.logger.log_indent == 3 and config.logger.log_max_width == 120


def test_change_log_directory(monkeypatch):
    """Test changing log directory"""
    monkeypatch.setattr("sys.argv", ["my_settings.py", "-l", os.path.expanduser("~/LOGS")])
    config = MySettings()
    assert config.log_directory == os.path.expanduser("~/LOGS")


def test_verbose(monkeypatch):
    """Test verbose mode"""
    monkeypatch.setattr("sys.argv", ["my_settings.py", "-v"])
    config = MySettings()
    assert config.log_level == logging.DEBUG


def test_show_version(monkeypatch):
    """Test show_version exits with a code of 2"""
    monkeypatch.setattr("sys.argv", ["my_settings.py", "-V"])
    config = MySettings()
    with pytest.raises(SystemExit) as error:
        config.show_version(package="pycommon", name="pycommon")
    assert error.type == SystemExit and error.value.code == 2


def test_quiet(monkeypatch):
    """Test quiet mode"""
    monkeypatch.setattr("sys.argv", ["my_settings.py", "-q"])
    config = MySettings()
    assert config.log_level == logging.WARNING


def test_extra_arguments(monkeypatch):
    """Test adding arguments to argv that settings doesn't care about"""
    params = ["my_settings.py", "-i", "test.txt", "-o", "output.txt"]
    params_plus = params + ["-v"]
    monkeypatch.setattr("sys.argv", params_plus)
    config = MySettings()
    argv = config.remaining_argv()
    assert argv == params and config.log_level == logging.DEBUG
