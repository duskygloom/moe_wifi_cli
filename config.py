import os
import json

from typing import Literal
from typing import TypedDict

config_file = "config.json"


class config_t(TypedDict):
    route: str
    username: str
    password: str
    session_id: str
    user_agent: str
    endpoints: dict[Literal["home", "login", "logout"], str]


def load_config() -> config_t:
    if not os.path.isfile(config_file):
        print(f"{config_file} does not exist.")
        return {}
    with open(config_file, 'r', encoding="utf-8") as fp:
        config = json.load(fp)
        return config


def save_config(config: config_t):
    with open(config_file, 'w', encoding="utf-8") as fp:
        json.dump(config, fp, ensure_ascii=False, indent='\t')


__all__ = [
    "load_config",
    "save_config"
]
