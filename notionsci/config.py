import logging
import os
import sys
from dataclasses import dataclass

import click
from appdirs import user_config_dir
from notion_client import Client
from pyzotero import zotero
from simple_parsing import Serializable

from notionsci.connections.notion import NotionClient
from notionsci.connections.zotero.client import ZoteroClient

CONFIG_VERSION = 1
APP_NAME = "notionsci"
DEFAULT_PROFLE = "default"
OVERRIDE_CONFIG_NAME = 'config.yml'


@dataclass
class NotionConfig(Serializable):
    token: str = ""

    def client(self) -> NotionClient:
        return NotionClient(client=Client(auth=self.token))


@dataclass
class ZoteroConfig(Serializable):
    token: str = ""
    library_type: str = "user"
    library_id: str = "123456"

    def client(self) -> ZoteroClient:
        return ZoteroClient(
            client=zotero.Zotero(self.library_id, self.library_type, self.token)
        )


@dataclass
class Connections(Serializable):
    notion: NotionConfig = NotionConfig()
    zotero: ZoteroConfig = ZoteroConfig()


@dataclass
class Config(Serializable):
    version: int = CONFIG_VERSION
    connections: Connections = Connections()


def load_config() -> Config:
    logging.basicConfig(level=logging.INFO)

    profile_arg = next(filter(lambda x: x.startswith('--profile='), sys.argv), None)
    if profile_arg:
        sys.argv.remove(profile_arg)
        profile_arg = profile_arg.replace('--profile=', '')

    profile = profile_arg or os.getenv('PROFILE', None) or DEFAULT_PROFLE
    config_name = f'{profile}.yml'

    # Determine correct config location
    if os.path.exists(OVERRIDE_CONFIG_NAME):
        config_path = OVERRIDE_CONFIG_NAME
        logging.info(f"Using overridden {OVERRIDE_CONFIG_NAME} in the current directory")
    else:
        config_path = os.path.join(user_config_dir(APP_NAME), config_name)
        if not os.path.exists(config_path):
            logging.info(f"No {profile} config detected.")
            logging.info(f"Creating default config in: {config_path}")
            logging.info(f"Please update the api tokens")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            Config().save(config_path)
            exit(0)

    # Try loading overridden config
    config: Config = Config.load(config_path)

    if not config.connections.notion.token:
        logging.error(f"Notion token should not be empty")
        logging.error(f"Update your config at: {config_path}")
        exit(1)

    return config


config: Config = load_config()
