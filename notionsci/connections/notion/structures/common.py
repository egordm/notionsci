import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Union

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.utils import UnionConvertor

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


EmojiFileType = Optional[Union[FileObject, EmojiObject]]

UnionEmojiFileConvertor = UnionConvertor(
    EmojiFileType,
    lambda x: FileObject.from_dict(x) if 'url' in x else EmojiObject.from_dict(x)
)


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
