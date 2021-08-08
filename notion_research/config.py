import os
from dataclasses import dataclass

from notion_client import Client
from pyzotero import zotero
from simple_parsing import Serializable


@dataclass
class NotionConfig(Serializable):
    token: str

    def client(self):
        return Client(auth=self.token)


@dataclass
class ZoteroConfig(Serializable):
    token: str
    library_type: str
    library_id: str

    def client(self):
        return zotero.Zotero(self.library_id, self.library_type, self.library_id);


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
