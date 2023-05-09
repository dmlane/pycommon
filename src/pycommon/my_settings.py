""" Settings data class which stores default settings and can be overriden from a toml file"""
import logging
import os
import sys

from pycommon.utils import Struct


class MySettings:  # pylint: disable=too-few-public-methods
    """Settings data class which stores default settings and can be overriden from a toml file"""

    def __init__(self):
        self.logger = Struct(
            log_app_name="net.dmlane",
            log_author="dave",
            log_indent=4,
            log_level=logging.INFO,
            log_max_width=88,
        )
        self.system = Struct(
            isatty=sys.stdout.isatty() or "PYCHARM_HOSTED" in os.environ,
        )

    def __repr__(self):
        pass

    # def read_toml_file(self, file_path):
    #     pass


nn = MySettings()
print("Done")
