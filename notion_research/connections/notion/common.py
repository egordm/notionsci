import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

Color = str
ID = str


class RichTextType(Enum):
    TEXT = 'text'
    MENTION = 'mention'
    EQUATION = 'equation'


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
    link: Optional[Dict]


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EquationObject:
    expression: str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class MentionObject:
    type: str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class RichText:
    plain_text: str
    annotations: Annotation
    type: RichTextType
    href: Optional[str] = None
    text: Optional[TextObject] = None
    equation: Optional[EquationObject] = None
    mention: Optional[MentionObject] = None


class PropertyType(Enum):
    TITLE = 'title'
    RICH_TEXT = 'rich_text'
    NUMBER = 'number'
    SELECT = 'select'
    MULTI_SELECT = 'multi_select'
    DATE = 'date'
    PEOPLE = 'people'
    FILES = 'files'
    CHECKBOX = 'checkbox'
    URL = 'url'
    EMAIL = 'email'
    PHONE_NUMBER = 'phone_number'
    FORMULA = 'formula'
    RELATION = 'relation'
    ROLLUP = 'rollup'
    CREATED_TIME = 'created_time'
    CREATED_BY = 'created_by'
    LAST_EDITED_TIME = 'last_edited_time'
    LAST_EDITED_BY = 'last_edited_by'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class SelectConfig:
    id: str
    name: str
    color: Color


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class DateConfig:
    start: str
    end: Optional[str]


TitleConfig = RichText
RichTextConfig = RichText
NumberConfig = int
MultiSelectConfig = List[SelectConfig]
PeopleConfig = List[Dict]
EmailConfig = str
CheckboxConfig = bool


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ValuedProperty:
    id: str
    type: PropertyType

    title: Optional[List[TitleConfig]] = None
    rich_text: Optional[List[RichTextConfig]] = None
    number: Optional[NumberConfig] = None
    select: Optional[SelectConfig] = None
    multi_select: Optional[MultiSelectConfig] = None
    date: Optional[DateConfig] = None
    people: Optional[PeopleConfig] = None
    files: Optional[Dict] = None
    checkbox: Optional[CheckboxConfig] = None
    url: Optional[Dict] = None
    email: Optional[EmailConfig] = None
    phone_number: Optional[Dict] = None
    formula: Optional[Dict] = None
    relation: Optional[Dict] = None
    rollup: Optional[Dict] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Property:
    id: str
    type: PropertyType
    name: str

    title: Optional[List[TitleConfig]] = None
    rich_text: Optional[List[RichTextConfig]] = None
    number: Optional[NumberConfig] = None
    select: Optional[SelectConfig] = None
    multi_select: Optional[MultiSelectConfig] = None
    date: Optional[DateConfig] = None
    people: Optional[PeopleConfig] = None
    files: Optional[Dict] = None
    checkbox: Optional[CheckboxConfig] = None
    url: Optional[Dict] = None
    email: Optional[EmailConfig] = None
    phone_number: Optional[Dict] = None
    formula: Optional[Dict] = None
    relation: Optional[Dict] = None
    rollup: Optional[Dict] = None

    created_time: Optional[dt.datetime] = None
    created_by: Optional[Dict] = None
    last_edited_time: Optional[dt.datetime] = None
    last_edited_by: Optional[Dict] = None


