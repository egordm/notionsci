import logging
import os
from dataclasses import dataclass

from appdirs import user_config_dir
from notion_client import Client
from pyzotero import zotero
from simple_parsing import Serializable

from notionsci.connections.notion import NotionClient
from notionsci.connections.zotero.client import ZoteroClient


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
    connections: Connections = Connections()


APP_NAME = "notionsci"
CONFIG_NAME = "config.yml"


def load_config() -> Config:
    logging.basicConfig(level=logging.INFO)

    # Determine correct config location
    if os.path.exists(CONFIG_NAME):
        config_path = CONFIG_NAME
        logging.info(f"Using overridden {CONFIG_NAME} in the current directory")
    else:
        config_path = os.path.join(user_config_dir(APP_NAME), CONFIG_NAME)
        if not os.path.exists(config_path):
            logging.info(f"No default config detected.")
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
