from dataclasses import dataclass
from typing import List, Optional

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notion_research.connections.notion.page import Page


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class DatabaseResult:
    object: str
    results: List[Page]
    next_cursor: Optional[str]
    has_more: bool


@dataclass
class Database:
    pass
