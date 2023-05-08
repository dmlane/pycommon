""" Test the logger module"""

import os
import shutil
import time

import pytest
from appdirs import user_log_dir
from logger import get_logger

from pycommon.my_config import config

APP_NAME = "net.dmlane.test"
AUTHOR = "dave"
LOG_DIR = user_log_dir(APP_NAME, AUTHOR)
LOG_NAME = "test_logger.log"


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup: fill with any logic you want
    config.common.log_directory = LOG_DIR
    config.common.isatty = False
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    yield  # this is where the testing happens
    shutil.rmtree(LOG_DIR, ignore_errors=True)

    # Teardown : fill with any logic you want


def test_log_created():
    """Tests that the logfile and its parent folder is created correctly"""
    logger = get_logger(
        name="test_logger",
        file_name=LOG_NAME,
        # app_name=APP_NAME,
        # author=AUTHOR,
        # log_level="INFO",
    )
    logger.info("test1234")
    assert os.path.exists(os.path.join(user_log_dir(APP_NAME, AUTHOR), LOG_NAME))


BACKUP_COUNT = 2


def test_log_cleanup():
    """Check that correct number of backup files are created"""
    logger = get_logger(
        name="test_logger",
        file_name=LOG_NAME,
        # app_name=APP_NAME,
        when="S",
        backup_count=BACKUP_COUNT,
        # author=AUTHOR,
        # log_level="INFO",
    )
    for msg in range(1, (BACKUP_COUNT * 8)):
        logger.info("test1234 .... %3d", msg)
        time.sleep(0.5)
    num_logs = 0
    for file_name in os.listdir(LOG_DIR):
        if file_name.startswith(LOG_NAME):
            num_logs += 1
    assert num_logs == (BACKUP_COUNT + 1), "Wrong number of backup files found"
