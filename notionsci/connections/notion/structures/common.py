import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Union, List

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.utils import UnionConvertor, ToMarkdownMixin, MarkdownContext, MarkdownBuilder, chain_to_markdown, \
    Undefinable, serde

Color = str
ID = str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class UserObject:
    object: str = 'user'
    id: Optional[ID] = None
    type: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    person: Optional[Dict] = None
    bot: Optional[Dict] = None


class RichTextType(Enum):
    text = 'text'
    mention = 'mention'
    equation = 'inline_equation'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Annotation:
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: Color

    def to_markdown(self, text) -> str:
        if self.bold:
            text = f'**{text}**'
        if self.italic:
            text = f'_{text}_'
        if self.strikethrough:
            text = f'~~{text}~~'
        if self.underline:
            text = f'<u>{text}</u>'
        if self.code:
            text = f'`{text}`'
        if self.color != 'default':
            text = f'<span style="color:{self.color}">{text}</span>'

        return text


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
class PageMention:
    id: ID


@serde()
@dataclass
class MentionObject:
    type: str
    user: Undefinable[UserObject] = None
    page: Undefinable[PageMention] = None

    def get_text(self) -> str:
        return self.type


@serde()
@dataclass
class RichText(ToMarkdownMixin):
    type: RichTextType

    plain_text: Undefinable[str] = None
    annotations: Undefinable[Annotation] = None
    href: Undefinable[str] = None
    text: Undefinable[TextObject] = None
    equation: Undefinable[EquationObject] = None
    mention: Undefinable[MentionObject] = None

    def raw_value(self):
        if self.type == RichTextType.text:
            return self.text
        elif self.type == RichTextType.mention:
            return self.mention
        elif self.type == RichTextType.equation:
            return self.equation

    def text_value(self) -> str:
        return self.raw_value().get_text()

    def to_markdown(self, context: MarkdownContext) -> str:
        result = ''
        if self.type == RichTextType.text:
            result = self.plain_text
        elif self.type == RichTextType.equation:
            result = MarkdownBuilder.inline_equation(self.equation.expression)
        elif self.type == RichTextType.mention:
            result = self.plain_text

        if self.href:
            result = MarkdownBuilder.url(self.href, result)

        if self.annotations:
            result = self.annotations.to_markdown(result)

        return result

    @staticmethod
    def from_text(text: str) -> 'RichText':
        return RichText(
            type=RichTextType.text,
            text=TextObject(
                content=text
            )
        )


class FileType(Enum):
    file = 'file'
    external = 'external'


@serde()
@dataclass
class FileTypeObject:
    url: str
    expiry_time: Optional[dt.datetime] = None


@serde()
@dataclass
class FileObject(ToMarkdownMixin):
    type: FileType
    caption: Undefinable[List[RichText]] = None
    file: Undefinable[FileTypeObject] = None
    external: Undefinable[FileTypeObject] = None
    name: Undefinable[str] = None  # Only filled for when used as property value

    def get_url(self) -> str:
        return self.file.url if self.type == FileType.file else self.external.url

    def to_markdown_caption(self, context: MarkdownContext) -> str:
        return chain_to_markdown(self.caption, context) if self.caption else None

    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.url(self.get_url(), self.name or self.to_markdown_caption(context))


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