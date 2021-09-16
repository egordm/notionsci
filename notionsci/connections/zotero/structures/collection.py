import datetime as dt
from dataclasses import dataclass
from typing import Dict, Optional

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

from notionsci.connections.zotero.structures import ID, ItemData, Links, Library, Meta, Entity


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class CollectionData(Entity):
    name: str
    parent_collection: Optional[ID] = None
    relations: Optional[Dict] = None

    @property
    def title(self):
        return self.name


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Collection(Entity):
    library: Library
    links: Links
    meta: Meta
    data: CollectionData

    children: Optional[Dict[ID, CollectionData]] = None
    items: Optional[Dict[ID, ItemData]] = None

    @property
    def title(self):
        return self.data.title

    def updated_at(self) -> dt.datetime:
        return dt.datetime.now()
