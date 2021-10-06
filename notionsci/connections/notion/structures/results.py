from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Union

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.blocks import Block
from notionsci.connections.notion.structures.content import Database, Page
from notionsci.utils import filter_none_dict, ListConvertor, UnionConvertor


def result_item_from_dict(x: dict):
    if x['object'] == 'page':
        return Page.from_dict(x)
    elif x['object'] == 'database':
        return Database.from_dict(x)
    elif x['object'] == 'block':
        return Block.from_dict(x)
    else:
        raise TypeError(f'Unexpected notion object type {x["object"]}')


ResultItem = Union[Page, Database, Block]
ResultConverter = ListConvertor(UnionConvertor(ResultItem, result_item_from_dict))


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[ResultConverter],
)
@dataclass
class QueryResult:
    object: str = 'list'
    results: List[ResultItem] = field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False


QueryFilter = Dict


class SortTimestamp(Enum):
    created_time = 'created_time'
    last_edited_time = 'last_edited_time'


class SortDirection(Enum):
    ascending = 'ascending'
    descending = 'descending'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class SortObject:
    direction: SortDirection
    timestamp: Optional[SortTimestamp] = None
    property: Optional[str] = None


def format_query_args(
        query: str = None,
        filter: Optional[QueryFilter] = None,
        sorts: Optional[List[SortObject]] = None,
        start_cursor: str = None,
        page_size: int = None
) -> dict:
    return filter_none_dict(dict(
        query=query,
        filter=filter if filter else None,
        sorts=[sort.to_dict() for sort in sorts] if sorts else None,
        start_cursor=start_cursor, page_size=page_size
    ))
