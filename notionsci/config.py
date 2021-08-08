import os
from dataclasses import dataclass

from notion_client import Client
from pyzotero import zotero
from simple_parsing import Serializable

from notionsci.connections.notion import NotionClient
from notionsci.connections.zotero.client import ZoteroClient


@dataclass
class NotionConfig(Serializable):
    token: str

    def client(self) -> NotionClient:
        return NotionClient(client=Client(auth=self.token))


@dataclass
class ZoteroConfig(Serializable):
    token: str
    library_type: str
    library_id: str

    def client(self) -> ZoteroClient:
        return ZoteroClient(client=zotero.Zotero(self.library_id, self.library_type, self.token))


@dataclass
class Connections(Serializable):
    notion: NotionConfig
    zotero: ZoteroConfig


@dataclass
class Config(Serializable):
    connections: Connections


def load_config() -> Config:
    # Try loading overridden config
    config: Config = Config.load('config.yml') if os.path.exists('config.yml') else None

    return config


config = load_config()
