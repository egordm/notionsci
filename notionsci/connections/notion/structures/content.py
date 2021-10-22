import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, TypeVar, Generic, Iterator, Any

import pandas as pd
from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.blocks import ChildrenMixin, BlockConvertor
from notionsci.connections.notion.structures.common import FileObject, ID, \
    UnionEmojiFileConvertor, EmojiFileType
from notionsci.connections.notion.structures.properties import PropertyDef, TitleValue, PropertyType, Property
from notionsci.utils import ToMarkdownMixin, MarkdownContext, chain_to_markdown, MarkdownBuilder, filter_not_none, \
    Undefinable, serde


class ParentType(Enum):
    database = 'database'
    page_id = 'page_id'
    workspace = 'workspace'


PT = TypeVar('PT', Property, PropertyDef)


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class HasPropertiesMixin(Generic[PT]):
    properties: Dict[str, PT] = field(default_factory=dict)

    def has_property(self, name: str):
        return name in self.properties

    def get_property(self, name: str) -> PT:
        return self.properties[name]

    def get_propery_raw_value(self, name: str, default=None) -> Optional[Any]:
        return self.get_property(name).raw_value() if name in self.properties else default

    def get_propery_value(self, name: str, default=None) -> Optional[Any]:
        return self.get_property(name).value() if name in self.properties else default

    def get_property_by_type(self, type: PropertyType) -> Iterator[PT]:
        return filter(lambda x: x.type == type, self.properties.values())

    def extend_properties(self, properties: Dict[str, PT]):
        self.properties = {
            **self.properties,
            **properties
        }


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Parent:
    type: ParentType
    database_id: Undefinable[ID] = None
    page_id: Undefinable[ID] = None
    workspace: Undefinable[bool] = None

    @staticmethod
    def page(id: ID) -> 'Parent':
        return Parent(type=ParentType.page_id, page_id=id)

    @staticmethod
    def database(id: ID) -> 'Parent':
        return Parent(type=ParentType.database, database_id=id)


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[UnionEmojiFileConvertor]
)
@dataclass
class ContentObject:
    object: str
    id: Optional[ID] = None
    parent: Optional[Parent] = None
    url: Optional[str] = None

    icon: EmojiFileType = None
    cover: Optional[FileObject] = None

    created_time: Optional[dt.datetime] = None
    last_edited_time: Optional[dt.datetime] = None


@serde(
    custom_type_convertors=[UnionEmojiFileConvertor, BlockConvertor],
    exclude=['children']
)
@dataclass
class Page(ContentObject, ToMarkdownMixin, ChildrenMixin, HasPropertiesMixin[Property]):
    object: str = 'page'

    properties: Dict[str, Property] = field(default_factory=dict)

    archived: bool = False

    def to_markdown(self, context: MarkdownContext) -> str:
        title = MarkdownBuilder.heading(self.get_title(), 'h1')
        prop_data = [
            {'Name': name, 'Value': prop.to_markdown(context)} for name, prop in self.properties.items()
            if prop.type != PropertyType.title
        ]
        props = MarkdownBuilder.table(pd.DataFrame(prop_data)) + '\n' if prop_data else None
        content = chain_to_markdown(self.children, context, sep='\n')

        return '\n'.join(filter_not_none([
            title, props, content
        ]))

    def get_title(self):
        return next(map(lambda x: x.value(), self.get_property_by_type(PropertyType.title)), '')


@serde(
    custom_type_convertors=[UnionEmojiFileConvertor],
    exclude=['children']
)
@dataclass
class Database(ContentObject, HasPropertiesMixin[PropertyDef]):
    object: str = 'database'
    title: Optional[TitleValue] = None

    properties: Dict[str, PropertyDef] = field(default_factory=dict)
