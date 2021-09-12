import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict

import pandas as pd
from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.blocks import ChildrenMixin, BlockConvertor
from notionsci.connections.notion.structures.common import FileObject, ID, \
    UnionEmojiFileConvertor, EmojiFileType
from notionsci.connections.notion.structures.properties import PropertyDef, TitleValue, PropertyType, Property
from notionsci.utils import ToMarkdownMixin, MarkdownContext, chain_to_markdown, MarkdownBuilder, filter_not_none


class ParentType(Enum):
    database = 'database'
    page_id = 'page_id'
    workspace = 'workspace'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Parent:
    type: ParentType
    database_id: Optional[ID] = None
    page_id: Optional[ID] = None
    workspace: Optional[bool] = None

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

    icon: EmojiFileType = None
    cover: Optional[FileObject] = None

    properties: Dict[str, Property] = field(default_factory=dict)
    created_time: Optional[dt.datetime] = None
    last_edited_time: Optional[dt.datetime] = None

    def get_property(self, name: str) -> Property:
        return self.properties[name]

    def extend_properties(self, properties: Dict[str, Property]):
        self.properties = {
            **self.properties,
            **properties
        }

    def get_title(self):
        prop = next(filter(lambda x: x.type == PropertyType.title, self.properties.values()), None)
        if prop is None:
            return ''
        else:
            return prop.value()


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[UnionEmojiFileConvertor, BlockConvertor]
)
@dataclass
class Page(ContentObject, ToMarkdownMixin, ChildrenMixin):
    object: str = 'page'
    url: Optional[str] = None

    archived: bool = False

    def to_markdown(self, context: MarkdownContext) -> str:
        title = MarkdownBuilder.heading(self.get_title(), 'h1')
        prop_data = [
            {'Name': name, 'Value': prop.value()} for name, prop in self.properties.items()
            if prop.type != PropertyType.title
        ]
        props = MarkdownBuilder.table(pd.DataFrame(prop_data)) + '\n' if prop_data else None

        content = chain_to_markdown(self.children, context, sep='\n')

        return '\n'.join(filter_not_none([
            title, props, content
        ]))


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[UnionEmojiFileConvertor]
)
@dataclass
class Database(ContentObject):
    object: str = 'database'
    title: Optional[TitleValue] = None
    properties: Dict[str, PropertyDef] = field(default_factory=dict)
