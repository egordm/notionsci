import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.common import RichText, Color, ID
from notionsci.utils import ExplicitNone, ToMarkdownMixin, MarkdownContext


class PropertyType(Enum):
    title = 'title'
    rich_text = 'rich_text'
    number = 'number'
    select = 'select'
    multi_select = 'multi_select'
    date = 'date'
    people = 'people'
    files = 'files'
    checkbox = 'checkbox'
    url = 'url'
    email = 'email'
    phone_number = 'phone_number'
    formula = 'formula'
    relation = 'relation'
    rollup = 'rollup'
    created_time = 'created_time'
    created_by = 'created_by'
    last_edited_time = 'last_edited_time'
    last_edited_by = 'last_edited_by'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class SelectValue:
    name: str
    id: Optional[str] = None
    color: Optional[Color] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class DateValue:
    start: str
    end: Optional[str] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class RelationItem:
    id: ID


TitleValue = List[RichText]
RichTextValue = List[RichText]
NumberValue = int
MultiSelectValue = List[SelectValue]
PeopleValue = List[Dict]
EmailValue = str
CheckboxValue = bool
CreatedTimeValue = dt.datetime
CreatedByValue = Dict
LastEditedTimeValue = dt.datetime
LastEditedByValue = Dict
UrlValue = str
RelationValue = List[RelationItem]


def object_to_text_value(raw_value: Any):
    if isinstance(raw_value, list):
        return ' '.join([object_to_text_value(v) for v in raw_value])
    elif isinstance(raw_value, RichText):
        return raw_value.text_value()
    return raw_value


def object_to_markdown(raw_value: Any, context: MarkdownContext, sep=' '):
    if isinstance(raw_value, list):
        return sep.join([object_to_markdown(v, context) for v in raw_value])
    elif isinstance(raw_value, RichText):
        return raw_value.to_markdown(context)
    elif isinstance(raw_value, SelectValue):
        return raw_value.name
    return raw_value


## Property Definition Types

@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Property(ToMarkdownMixin):
    type: PropertyType

    id: Optional[str] = None
    title: Optional[TitleValue] = None

    rich_text: Optional[RichTextValue] = None
    number: Optional[NumberValue] = None
    select: Optional[SelectValue] = None
    multi_select: Optional[MultiSelectValue] = None
    date: Optional[DateValue] = None
    people: Optional[PeopleValue] = None
    files: Optional[Dict] = None
    checkbox: Optional[CheckboxValue] = None
    url: Optional[UrlValue] = None
    email: Optional[EmailValue] = None
    phone_number: Optional[Dict] = None
    formula: Optional[Dict] = None
    relation: Optional[RelationValue] = None
    rollup: Optional[Dict] = None
    created_time: Optional[CreatedTimeValue] = None
    created_by: Optional[CreatedByValue] = None
    last_edited_time: Optional[LastEditedTimeValue] = None
    last_edited_by: Optional[LastEditedByValue] = None

    def _value(self):
        return getattr(self, self.type.value)

    def raw_value(self):
        if self.type == PropertyType.date:
            return dt.datetime.fromisoformat(self.date.start)
        else:
            return self._value()

    def value(self):
        return object_to_text_value(self.raw_value())

    def to_markdown(self, context: MarkdownContext) -> str:
        return object_to_markdown(
            self._value(), context,
            sep=',+ ' if self.type == PropertyType.multi_select else ' '
        )

    @staticmethod
    def as_title(text: str) -> 'Property':
        return Property(
            type=PropertyType.title,
            title=[RichText.from_text(text)]
        )

    @staticmethod
    def as_url(text: str) -> 'Property':
        return Property(
            type=PropertyType.url,
            url=text if text else ExplicitNone()
        )

    @staticmethod
    def as_number(number: int) -> 'Property':
        return Property(
            type=PropertyType.number,
            number=number
        )

    @staticmethod
    def as_date(date: dt.datetime) -> 'Property':
        return Property(
            type=PropertyType.date,
            date=DateValue(date.isoformat())
        )

    @staticmethod
    def as_rich_text(text: str) -> 'Property':
        # Max length = 2000
        return Property(
            type=PropertyType.rich_text,
            rich_text=[RichText.from_text((text or '')[:2000])]
        )

    @staticmethod
    def as_select(value: str) -> 'Property':
        return Property(
            type=PropertyType.select,
            select=SelectValue(name=value)
        )

    @staticmethod
    def as_multi_select(values: List[str]) -> 'Property':
        return Property(
            type=PropertyType.multi_select,
            multi_select=[
                SelectValue(name=value)
                for value in values
            ]
        )

    @staticmethod
    def as_relation(relations: RelationValue) -> 'Property':
        return Property(
            type=PropertyType.relation,
            relation=relations
        )


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class SelectDef:
    options: List[SelectValue]


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class RelationDef:
    database_id: ID
    synced_property_name: Optional[str] = None
    synced_property_id: Optional[str] = None


TitleDef = Dict
RichTextDef = Dict
NumberDef = Dict
PeopleDef = List[Dict]
EmailDef = Dict
CheckboxDef = Dict
CreatedTimeDef = Dict
CreatedByDef = Dict
LastEditedTimeDef = Dict
LastEditedByDef = Dict
UrlDef = Dict
DateDef = Dict
MultiSelectDef = SelectDef


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class PropertyDef:
    type: PropertyType
    id: Optional[str] = None
    name: Optional[str] = None

    title: Optional[TitleDef] = None
    rich_text: Optional[RichTextDef] = None
    number: Optional[NumberDef] = None
    select: Optional[SelectDef] = None
    multi_select: Optional[MultiSelectDef] = None
    date: Optional[DateDef] = None
    people: Optional[PeopleDef] = None
    files: Optional[Dict] = None
    checkbox: Optional[CheckboxDef] = None
    url: Optional[UrlDef] = None
    email: Optional[EmailDef] = None
    phone_number: Optional[Dict] = None
    formula: Optional[Dict] = None
    relation: Optional[RelationDef] = None
    rollup: Optional[Dict] = None
    created_time: Optional[CreatedTimeDef] = None
    created_by: Optional[CreatedByDef] = None
    last_edited_time: Optional[LastEditedTimeDef] = None
    last_edited_by: Optional[LastEditedByDef] = None

    @staticmethod
    def as_title() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.title, title={})

    @staticmethod
    def as_url() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.url, url={})

    @staticmethod
    def as_rich_text() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.rich_text, rich_text={})

    @staticmethod
    def as_select() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.select, select=SelectDef(options=[]))

    @staticmethod
    def as_multi_select() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.multi_select, multi_select=SelectDef(options=[]))

    @staticmethod
    def as_last_edited_time() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.last_edited_time, last_edited_time={})

    @staticmethod
    def as_date() -> 'PropertyDef':
        return PropertyDef(type=PropertyType.date, date={})

    @staticmethod
    def as_relation(database: ID) -> 'PropertyDef':
        return PropertyDef(type=PropertyType.relation, relation=RelationDef(database))
