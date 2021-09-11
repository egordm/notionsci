import datetime as dt
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Any

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.common import FileObject, RichText, ID
from notionsci.utils import ForwardRefConvertor, ListConvertor, ToMarkdownMixin, Markdown


class BlockType(Enum):
    paragraph = 'paragraph'
    heading_1 = 'heading_1'
    heading_2 = 'heading_2'
    heading_3 = 'heading_3'
    bulleted_list_item = 'bulleted_list_item'
    numbered_list_item = 'numbered_list_item'
    to_do = 'to_do'
    toggle = 'toggle'
    child_page = 'child_page'
    embed = 'embed'
    image = 'image'
    video = 'video'
    file = 'file'
    pdf = 'pdf'
    bookmark = 'bookmark'
    unsupported = 'unsupported'


BlockConvertor = ListConvertor(ForwardRefConvertor('Block'))


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class ParagraphBlock(ToMarkdownMixin):
    text: List[RichText]
    children: Optional[List['Block']] = None

    def to_markdown(self, context: Any) -> str:
        return ''.join([
            part.to_markdown(context) for part in self.text
        ]) + '\n'


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class ListBlock(ToMarkdownMixin):
    text: List[RichText]
    children: Optional[List['Block']] = None

    def to_markdown(self, context: Any) -> str:
        return ''.join([t.to_markdown(context) for t in self.text])


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class TodoBlock(ListBlock):
    checked: Optional[bool] = None

    def to_markdown(self, context: Any) -> str:
        text = super().to_markdown(context)
        return f'[x] {text}' if self.checked else f'[ ] {text}'


@dataclass
class HeadingBlock(ToMarkdownMixin):
    text: List[RichText]

    def to_markdown(self, context: Any) -> str:
        return ''.join([
            part.to_markdown(context) for part in self.text
        ])


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ChildPageBlock:
    text: str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EmbedBlock(ToMarkdownMixin):
    url: str
    caption: List[RichText]

    def to_markdown(self, context: Any) -> str:
        return Markdown.build_embed(
            url=self.url,
            caption=''.join([t.to_markdown(context) for t in self.caption]) if self.caption else None
        )


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class BookmarkBlock(EmbedBlock):
    pass


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading1Block(HeadingBlock):
    def to_markdown(self, context: Any) -> str:
        return f'# {super().to_markdown(context)}\n'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading2Block(HeadingBlock):
    def to_markdown(self, context: Any) -> str:
        return f'## {super().to_markdown(context)}\n'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading3Block(HeadingBlock):
    def to_markdown(self, context: Any) -> str:
        return f'### {super().to_markdown(context)}\n'


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ImageBlock(FileObject):
    def to_markdown(self, context: Any) -> str:
        return Markdown.build_image(
            url=self.get_url(),
            caption=self.to_markdown_caption(context))


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class PdfBlock(FileObject):
    def to_markdown(self, context: Any) -> str:
        return Markdown.build_embed(
            url=f'https://docs.google.com/viewer?url={urllib.parse.quote_plus(self.get_url())}&embedded=true',
            caption=self.to_markdown_caption(context) or ' ')


BulletedListBlock = ListBlock
NumberedListBlock = ListBlock
ToggleBlock = ListBlock

FileBlock = FileObject
VideoBlock = FileObject


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Block(ToMarkdownMixin):
    object: str = 'block'
    id: Optional[ID] = None
    type: Optional[BlockType] = None

    created_time: Optional[dt.datetime] = None
    last_edited_time: Optional[dt.datetime] = None

    archived: bool = False
    has_children: bool = True

    paragraph: Optional[ParagraphBlock] = None
    heading_1: Optional[Heading1Block] = None
    heading_2: Optional[Heading2Block] = None
    heading_3: Optional[Heading3Block] = None
    bulleted_list_item: Optional[BulletedListBlock] = None
    numbered_list_item: Optional[NumberedListBlock] = None
    to_do: Optional[TodoBlock] = None
    toggle: Optional[ToggleBlock] = None
    child_page: Optional[ChildPageBlock] = None
    embed: Optional[EmbedBlock] = None
    image: Optional[ImageBlock] = None
    video: Optional[VideoBlock] = None
    file: Optional[FileBlock] = None
    pdf: Optional[PdfBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    unsupported: Optional[str] = None

    def to_markdown(self, context: Any) -> str:
        if self.type == BlockType.paragraph:
            return self.paragraph.to_markdown(context)
        elif self.type == BlockType.heading_1:
            return self.heading_1.to_markdown(context)
        elif self.type == BlockType.heading_2:
            return self.heading_2.to_markdown(context)
        elif self.type == BlockType.heading_3:
            return self.heading_3.to_markdown(context)
        elif self.type == BlockType.image:
            return self.image.to_markdown(context)
        elif self.type == BlockType.bulleted_list_item:
            return f'* {self.bulleted_list_item.to_markdown(context)}'
        elif self.type == BlockType.numbered_list_item:
            return f'1. {self.numbered_list_item.to_markdown(context)}'
        elif self.type == BlockType.to_do:
            return self.to_do.to_markdown(context)
        elif self.type == BlockType.embed:
            return self.embed.to_markdown(context)
        elif self.type == BlockType.pdf:
            return self.pdf.to_markdown(context)
        elif self.type == BlockType.bookmark:
            return self.bookmark.to_markdown(context)
        elif self.type == BlockType.unsupported:
            return 'Unsupported Block Type!\n'
        else:
            raise Exception('unsupported! ' + self.type.value)
