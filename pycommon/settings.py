""" Fetch data from config file """
import os
import tomllib
from importlib import resources

import appdirs
from my_exceptions import MyException
from utils import dict_merge

# The first file in PREFERRED_CONFIG_LOCATIONS will be used
PREFERRED_CONFIG_LOCATIONS = [
    str(resources.files("pycommon")) + "/data",
    appdirs.user_config_dir(appname="dmlane"),
]
CONFIG_DIR = appdirs.user_config_dir(appname="dmlane")
CONFIG_NAME = "config.toml"
os.makedirs(CONFIG_DIR, exist_ok=True)


class Settings:
    """Handle settings from config file"""

    def __init__(self, package: str = None, toml: str = None):
        self.config = {}
        self.config_file = None
        for location in PREFERRED_CONFIG_LOCATIONS:
            self.load_config(os.path.join(location, CONFIG_NAME))

        # Handle the project specific settings
        # if package is not None:
        #     self.load_config(str(resources.files(package)) + "/data/" + toml)
        #     self.load_config(appdirs.user_config_dir(appname="dmlane") + "/" + toml)
        # if not self.config:
        #     raise FileNotFoundError(
        #         f"Could not find config file '{CONFIG_NAME}' in {PREFERRED_CONFIG_LOCATIONS}"
        #     )

    def load_config(self, config_file):
        """Load settings from config file"""
        try:
            with open(config_file, "rb") as handle:
                config = tomllib.load(handle)
        except FileNotFoundError:
            return
        except tomllib.TOMLDecodeError as exc:
            raise MyException(f"Could not load config file {config_file}  (TOML Error)") from exc

        dict_merge(self.config, config)
        self.config_file = config_file


settings = Settings()
if __name__ == "__main__":
    print(settings.config)
