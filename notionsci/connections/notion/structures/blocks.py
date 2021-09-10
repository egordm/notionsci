import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.common import FileObject, RichText, ID
from notionsci.utils import ForwardRefConvertor, ListConvertor


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
class ParagraphBlock:
    text: List[RichText]
    children: Optional[List['Block']] = None


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class ListBlock:
    text: List[RichText]
    children: Optional[List['Block']] = None


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class TodoBlock(ListBlock):
    checked: Optional[bool] = None


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class HeadingBlock:
    text: List[RichText]


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ChildPageBlock:
    text: str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EmbedBlock:
    url: str


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class BookmarkBlock:
    url: str
    caption: List[RichText]


Heading1Block = HeadingBlock
Heading2Block = HeadingBlock
Heading3Block = HeadingBlock

BulletedListBlock = ListBlock
NumberedListBlock = ListBlock
ToggleBlock = ListBlock

FileBlock = FileObject
ImageBlock = FileObject
VideoBlock = FileObject
PdfBlock = FileObject


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Block:
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
