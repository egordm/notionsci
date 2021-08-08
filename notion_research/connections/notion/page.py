import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notion_research.connections.notion.common import ID, ValuedProperty


class ParentType(Enum):
    DATABASE = 'database'
    PAGE = 'page'
    WORKSPACE = 'workspace'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Parent:
    type: ParentType
    database_id: Optional[ID] = None
    page_id: Optional[ID] = None
    workspace: Optional[bool] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Page:
    id: Optional[ID] = None
    object: str = 'page'
    url: Optional[str] = None
    parent: Optional[Parent] = None

    properties: Dict[str, ValuedProperty] = field(default_factory=dict)
    children: Optional[List[Dict]] = None

    archived: bool = False
    created_time: Optional[dt.datetime] = None
    last_edited_time: Optional[dt.datetime] = None
