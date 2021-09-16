from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

from notionsci.connections.zotero.structures import ID
from notionsci.utils import filter_none_dict


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class SearchParameters:
    item_key: Optional[List[ID]] = None
    item_type: Optional[str] = None
    q: Optional[str] = None
    since: Optional[int] = None
    tag: Optional[str] = None

    include_trashed: Optional[int] = None

    def to_query(self):
        if isinstance(self.item_key, list):
            self.item_key = ','.join(self.item_key)

        return filter_none_dict(self.to_dict())


class Direction(Enum):
    asc = 'asc'
    desc = 'desc'


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class SearchPagination:
    sort: Optional[str] = None
    direction: Optional[Direction] = None
    limit: int = 100
    start: int = 0

    def to_query(self):
        return filter_none_dict(self.to_dict())
