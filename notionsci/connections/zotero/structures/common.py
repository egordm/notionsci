from dataclasses import dataclass
from typing import Dict, Optional

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

ID = str
Links = Dict
User = Dict


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Meta:
    created_by_user: Optional[User] = None
    parsed_date: Optional[str] = None
    creator_summary: Optional[str] = None
    num_items: Optional[int] = None
    num_collections: Optional[int] = None
    num_children: Optional[int] = None


@dataclass
class Entity:
    key: ID
    version: int
