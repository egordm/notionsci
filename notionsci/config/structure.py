from dataclasses import dataclass

from notion_client import Client
from simple_parsing import Serializable

from notionsci.config.constants import CONFIG_VERSION, TEMPLATE_ZOTERO, DEV_TESTS_PAGE
from notionsci.connections import zotero
from notionsci.connections.notion import NotionClient
from notionsci.connections.notion_unofficial import NotionUnofficialClient
from notionsci.connections.zotero import ZoteroClient

ERROR_CONNECTION = 'This command requires access to {} api\nConfigure it first at connections.{}'


@dataclass
class NotionUnofficialConfig(Serializable):
    token_v2: str = "<notion unofficial token_v2>"

    def client(self) -> NotionUnofficialClient:
        if not self.token_v2 or 'notion unofficial token_v2' in self.token_v2:
            raise Exception(ERROR_CONNECTION.format('Notion Unofficial', 'notion_unofficial'))

        return NotionUnofficialClient(token_v2=self.token_v2)


@dataclass
class NotionConfig(Serializable):
    token: str = "<notion token>"

    def client(self) -> NotionClient:
        if not self.token or 'notion token' in self.token:
            raise Exception(ERROR_CONNECTION.format('Notion Official', 'notion'))

        return NotionClient(client=Client(auth=self.token))


@dataclass
class ZoteroConfig(Serializable):
    token: str = "<zotero token>"
    library_type: str = "user"
    library_id: str = "123456"

    def client(self) -> ZoteroClient:
        if not self.token or 'zotero token' in self.token:
            raise Exception(ERROR_CONNECTION.format('Zotero', 'zotero'))

        return ZoteroClient(client=zotero.Zotero(self.library_id, self.library_type, self.token))


@dataclass
class Connections(Serializable):
    notion_unofficial: NotionUnofficialConfig = NotionUnofficialConfig()
    notion: NotionConfig = NotionConfig()
    zotero: ZoteroConfig = ZoteroConfig()


@dataclass
class Templates(Serializable):
    zotero_template: str = TEMPLATE_ZOTERO


@dataclass
class Development(Serializable):
    test_page: str = DEV_TESTS_PAGE


@dataclass
class Config(Serializable):
    version: int = CONFIG_VERSION
    connections: Connections = Connections()
    templates: Templates = Templates()
    development: Development = Development()
