from os.path import abspath, dirname, join

import toml
from pydantic import BaseModel, FilePath

from ..utils.patterns import singleton

CURRENT_DIR = dirname(abspath(__file__))


@singleton
class ConfigFile(BaseModel):
    file_path: FilePath = join(CURRENT_DIR, "conf_project.toml")

    def get_config_toml(self) -> dict[str, str]:
        return toml.load(self.file_path)


CONFIG_TOML = ConfigFile().get_config_toml()
