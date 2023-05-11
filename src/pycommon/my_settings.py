""" Settings data class which stores default settings and can be overriden from a toml file"""
import argparse
import logging
import os
import sys
import tomllib
from importlib import metadata, resources

import appdirs

from pycommon.utils import Struct, dict_merge


class MySettings:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Settings data class which stores default settings and can be overriden from a toml file"""

    def __init__(self):
        self.logger = Struct()
        self._config = {}
        self._log_level = logging.INFO
        self._override_config_file = None
        self._display_version = False
        self._log_directory = None
        self._remaining_argv = [sys.argv[0]]
        self._isatty = sys.stdout.isatty() or "PYCHARM_HOSTED" in os.environ
        self.process_arguments()
        self.load_toml_file()

    def process_arguments(self):
        """Process sepecific command line arguments"""
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)
        args = parser.parse_known_args()
        self._log_level = args[0].log_level
        self._override_config_file = args[0].config_file
        self._log_directory = args[0].log_directory
        self._display_version = args[0].display_version
        self._remaining_argv += args[1]  # These arguments can be parsed again by the caller

    @staticmethod
    def add_arguments(parser):
        """Add arguments to parser"""

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            const=logging.WARNING,
            dest="log_level",
            default=logging.INFO,
            help="Decrease logging level to WARNING",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_const",
            const=logging.DEBUG,
            dest="log_level",
            default=logging.INFO,
            help="Increase logging level to DEBUG",
        )
        parser.add_argument(
            "--config-file",
            action="store",
            dest="config_file",
            default=appdirs.user_config_dir("dmlane", "dave") + "/settings.toml",
            help="Override config file",
        )
        parser.add_argument(
            "-l",
            "--log-directory",
            action="store",
            dest="log_directory",
            default=None,
            help="Override log directory",
        )
        parser.add_argument(
            "-V",
            "--version",
            action="store_true",
            dest="display_version",
            default=False,
            help="Print version information and exit",
        )

    def remaining_argv(self):
        """Return the remaining command line arguments"""
        return self._remaining_argv

    def load_toml_file(self, package_name="pycommon"):
        """Read a toml file and add it to self._config"""

        for config_file in [
            str(resources.files(package_name)) + "/data/settings.toml",
            self._override_config_file,
        ]:
            try:
                with open(config_file, "rb") as handle:
                    local_settings = tomllib.load(handle)
                dict_merge(self._config, local_settings)

            except FileNotFoundError:
                if self._log_level <= logging.DEBUG:
                    print(f"No settings file found in {package_name} ({config_file})")
            except tomllib.TOMLDecodeError:
                print(f"Error reading settings file in {package_name} ({config_file})")
                raise
        for key, value in self._config.items():
            if isinstance(value, dict):
                setattr(self, key, Struct(**value))
            else:
                setattr(self, key, value)

    @property
    def log_directory(self):
        """Return the log directory"""
        if self._log_directory is None:
            self._log_directory = appdirs.user_log_dir(
                self.logger.log_app_name, self.logger.log_author
            )
        return self._log_directory

    @property
    def isatty(self):
        """Return True if the terminal is a tty"""
        return self._isatty

    @property
    def log_level(self):
        """Return the log level"""
        return self._log_level

    def show_version(self, package, name):
        """Display version information and exit if --version is specified"""
        if self._display_version:
            print(f"{name} - version {metadata.version(package)}")
            sys.exit(2)


config = MySettings()
