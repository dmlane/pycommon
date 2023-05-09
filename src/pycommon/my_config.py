""" Set config for use by pycommon - can/should be extended """
import copy
import logging
import os
import sys
from importlib import resources

import appdirs
import tomlkit
import utils

CONFIG_DIR = appdirs.user_config_dir("dmlane", "dave")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.toml")
DEFAULT_CONFIG_DIR = str(resources.files("pycommon")) + "/data"
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "settings.toml")


class MyConfig:  # pylint: disable=too-few-public-methods
    """Set config for use by pycommon - can/should be extended"""

    # TODO: We want to separate unchangeable config from things that can go in the toml file, \
    #       but present everything together
    # TODO: Add a method to add system and user settings from an application - probably using TABLE?
    # TODO: We want to merge toml documents complete with comments, so stop merging dicts.
    def __init__(self):
        # System settings which will never go in the TOML
        self.system_settings = {
            "log_app_name": "net.dmlane",
            "log_author": "dave",
            "log_indent": 4,
            "log_level": logging.INFO,
            "log_max_width": 88,
            "isatty": sys.stdout.isatty() or "PYCHARM_HOSTED" in os.environ,
        }
        # Load the settings from the TOML file(s)
        self.user_settings = {}
        user_settings = self.load_toml(DEFAULT_CONFIG_FILE)
        utils.dict_merge(user_settings, dict(self.load_toml(CONFIG_FILE)))
        self.user_settings = user_settings

        self.all_settings = copy.deepcopy(self.system_settings)
        utils.dict_merge(self.all_settings, self.user_settings)
        self.common = utils.Struct(**self.all_settings)

    @staticmethod
    def load_toml(config_file) -> tomlkit.document:
        """Load settings from a TOML file"""

        try:
            with open(config_file, "r", encoding="utf-8") as handle:
                current_config = tomlkit.loads(handle.read())
        except FileNotFoundError:
            current_config = tomlkit.loads("")
        return current_config

    def process_verbose_args(self):
        """Change debug level if quiet/verbose flag is set"""
        for arg in sys.argv[1:]:
            if arg in ("-q", "--quiet"):
                self.common.log_level = logging.WARNING
                sys.argv.remove(arg)
            elif arg in ("-v", "--verbose"):
                self.common.log_level = logging.DEBUG
                sys.argv.remove(arg)

    def create_settings_file(self, config_file=None):
        """Create settings file - this will only add keys which are not already present"""

        if config_file is None:
            config_file = CONFIG_FILE
        try:
            with open(config_file, "r", encoding="utf-8") as handle:
                current_config = tomlkit.loads(handle.read())
        except FileNotFoundError:
            current_config = tomlkit.loads("")
        changed = False
        for attr, value in self.__dict__.items():
            if attr.startswith("_") or callable(attr):
                continue
            if attr not in current_config:
                current_config.add(attr, value)
                changed = True
        if not changed:
            return

        with open(config_file, "w", encoding="utf-8") as handle:
            tomlkit.dump(current_config, handle, sort_keys=True)
            # handle.write(res)


_config = MyConfig()
config = _config.all_settings
# print(config)
# config.create_settings_file()
