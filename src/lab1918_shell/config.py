import configparser
from pathlib import Path
from typing import Dict


class Config:
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".lab1918"
        self.config_file = self.config_dir / "shell.ini"

    @property
    def default_config(self):
        config = configparser.ConfigParser()
        config["default"] = {
            "api_server": "api.lab1918.com",
            "api_key": "<replace with api key>",
        }
        return config

    def config_file_exist(self):
        return self.config_file.is_file()

    def ensure_default_config(self):
        if self.config_file_exist():
            return

        self.config_dir.mkdir(parents=True, exist_ok=True)
        with self.config_file.open(mode="w") as f:
            self.default_config.write(f)

    def get_config(self, profile: str) -> Dict:
        self.ensure_default_config()
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if profile not in config:
            return {}
        return dict(config[profile])
