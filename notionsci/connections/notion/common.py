import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Union, Any

from dataclass_dict_convert import dataclass_dict_convert
from dataclass_dict_convert.convert import SimpleTypeConvertor
from stringcase import snakecase

from notionsci.utils import filter_none_dict, ExplicitNone

Color = str
ID = str


class RichTextType(Enum):
    text = 'text'
    mention = 'mention'
    equation = 'equation'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Annotation:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class TextObject:
    content: str
    link: Optional[Dict] = None

    def get_text(self) -> str:
        return self.content


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EquationObject:
    expression: str

    def get_text(self) -> str:
        return self.expression


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class MentionObject:
    type: str

    def get_text(self) -> str:
        return self.type


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class RichText:
    type: RichTextType
    plain_text: Optional[str] = None
    annotations: Optional[str] = None
    href: Optional[str] = None
    text: Optional[TextObject] = None
    equation: Optional[EquationObject] = None
    mention: Optional[MentionObject] = None

    def raw_value(self):
        if self.type == RichTextType.text:
            return self.text
        elif self.type == RichTextType.mention:
            return self.mention
        elif self.type == RichTextType.equation:
            return self.equation

    def text_value(self) -> str:
        return self.raw_value().get_text()

    @staticmethod
    def from_text(text: str) -> 'RichText':
        return RichText(
            type=RichTextType.text,
            text=TextObject(
                content=text
            )
        )


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


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Property:
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

    def raw_value(self):
        if self.type == PropertyType.title:
            return self.title
        elif self.type == PropertyType.rich_text:
            return self.rich_text
        elif self.type == PropertyType.number:
            return self.number
        elif self.type == PropertyType.select:
            return self.select
        elif self.type == PropertyType.multi_select:
            return self.multi_select
        elif self.type == PropertyType.date:
            return dt.datetime.fromisoformat(self.date.start)
        elif self.type == PropertyType.people:
            return self.people
        elif self.type == PropertyType.files:
            return self.files
        elif self.type == PropertyType.checkbox:
            return self.checkbox
        elif self.type == PropertyType.url:
            return self.url
        elif self.type == PropertyType.email:
            return self.email
        elif self.type == PropertyType.phone_number:
            return self.phone_number
        elif self.type == PropertyType.formula:
            return self.formula
        elif self.type == PropertyType.relation:
            return self.relation
        elif self.type == PropertyType.rollup:
            return self.rollup
        elif self.type == PropertyType.created_time:
            return self.created_time
        elif self.type == PropertyType.created_by:
            return self.created_by
        elif self.type == PropertyType.last_edited_time:
            return self.last_edited_time
        elif self.type == PropertyType.last_edited_by:
            return self.last_edited_by

    def value(self):
        return object_to_text_value(self.raw_value())

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


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ContentObject:
    object: str
    id: Optional[ID] = None
    parent: Optional[Parent] = None

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


class FileType(Enum):
    file = 'file'
    external = 'external'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class FileObject:
    type: FileType
    url: str
    expiry_time: Optional[dt.datetime] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EmojiObject:
    emoji: str
    type: str = 'emoji'


def emoji_from_dict_converter(x: dict):
    if not x: return None
    if x['type'] == 'emoji':
        return EmojiObject.from_dict(x)
    else:
        return FileObject.from_dict(x)


def emoji_to_dict_converter(x: Union[FileObject, EmojiObject]):
    if not x: return None
    if isinstance(x, FileObject):
        return FileObject.to_dict(x)
    else:
        return EmojiObject.to_dict(x)


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[SimpleTypeConvertor(
        type=Optional[Union[FileObject, EmojiObject]],
        to_dict=emoji_from_dict_converter,
        from_dict=emoji_from_dict_converter
    )]
)
@dataclass
class Page(ContentObject):
    object: str = 'page'
    url: Optional[str] = None
    icon: Optional[Union[FileObject, EmojiObject]] = None
    cover: Optional[FileObject] = None

    children: Optional[List[Dict]] = None

    archived: bool = False


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Database(ContentObject):
    object: str = 'database'
    title: Optional[TitleValue] = None
    properties: Dict[str, PropertyDef] = field(default_factory=dict)


def result_from_dict_converter():
    def wrap(val: List[dict]):
        result = []

        for item in val:
            if item['object'] == 'page':
                result.append(Page.from_dict(item))
            elif item['object'] == 'database':
                result.append(Database.from_dict(item))
            else:
                raise TypeError(f'Unexpected notion object type {item["object"]}')
        return result

    return wrap


def result_to_dict_converter():
    def wrap(val: List[Union[Page, Database]]):
        return [item.to_dict() for item in val]

    return wrap


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_from_dict_convertors={
        'results': result_from_dict_converter()
    },
    custom_to_dict_convertors={
        'results': result_to_dict_converter()
    },
)
@dataclass
class QueryResult:
    object: str = 'list'
    results: List[Union[Page, Database]] = field(default_factory=list)
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
        filter: Optional[QueryFilter] = None,
        sorts: Optional[List[SortObject]] = None,
        start_cursor: str = None,
        page_size: int = None
) -> dict:
    return filter_none_dict(dict(
        filter=filter if filter else None,
        sorts=[sort.to_dict() for sort in sorts] if sorts else None,
        start_cursor=start_cursor, page_size=page_size
    ))
