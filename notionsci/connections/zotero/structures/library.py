from dataclasses import dataclass
from enum import Enum

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

from notionsci.connections.zotero.structures import Links


class LibraryType(Enum):
    group = 'group'
    user = 'user'


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Library:
    id: int
    type: LibraryType
    name: str
    links: Links