import datetime as dt
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Union

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import snakecase

from notionsci.connections.notion.structures.common import FileObject, RichText, ID
from notionsci.utils import ForwardRefConvertor, ListConvertor, ToMarkdownMixin, MarkdownBuilder, MarkdownContext, \
    chain_to_markdown
from notionsci.utils.markdown import MarkdownListType


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


@dataclass
class ChildrenMixin:
    children: Optional[List['Block']] = None

    def set_children(self, children: List['Block']):
        self.children = children

    def get_children(self) -> List['Block']:
        return self.children


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class ParagraphBlock(ToMarkdownMixin, ChildrenMixin):
    text: List[RichText] = field(default_factory=list)

    def to_markdown(self, context: MarkdownContext) -> str:
        return chain_to_markdown(self.text, context)


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class ListBlock(ToMarkdownMixin, ChildrenMixin):
    text: List[RichText] = field(default_factory=list)

    def to_markdown(self, context: MarkdownContext) -> str:
        prefix = self._prefix() * (context.depth + 1)
        children = chain_to_markdown(
            self.children,
            context.copy(depth=context.depth + 1, counter=1),
            sep='\n', prefix=prefix
        ) if self.get_children() else None
        content = self._markdown_format_fn()(chain_to_markdown(self.text, context.copy(counter=1)), context)

        return f'{content}\n{children}' if children else content

    def _prefix(self) -> str:
        return '  '

    def _markdown_format_fn(self):
        return lambda x, ctx: x


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class BulletedListBlock(ListBlock):
    def _markdown_format_fn(self):
        return lambda x, ctx: MarkdownBuilder.list(x, ctx, MarkdownListType.bullet)


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class NumberedListBlock(ListBlock):
    def _markdown_format_fn(self):
        return lambda x, ctx: MarkdownBuilder.list(x, ctx, MarkdownListType.numeric)

    def countable(self) -> bool:
        return True

    def _prefix(self) -> str:
        return '    '


@dataclass_dict_convert(
    dict_letter_case=snakecase,
    custom_type_convertors=[BlockConvertor]
)
@dataclass
class TodoBlock(ListBlock):
    checked: Optional[bool] = None

    def _markdown_format_fn(self):
        return lambda x, ctx: MarkdownBuilder.todo(x, self.checked)


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ChildPageBlock:
    text: str


@dataclass
class HeadingBlock(ToMarkdownMixin):
    text: List[RichText]

    def to_markdown(self, context: MarkdownContext) -> str:
        return chain_to_markdown(self.text, context)


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading1Block(HeadingBlock):
    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.heading(super().to_markdown(context), 'h1')


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading2Block(HeadingBlock):
    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.heading(super().to_markdown(context), 'h2')


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class Heading3Block(HeadingBlock):
    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.heading(super().to_markdown(context), 'h3')


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class EmbedBlock(ToMarkdownMixin):
    url: str
    caption: List[RichText]

    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.embed(
            url=self.url,
            caption=chain_to_markdown(self.caption, context) if self.caption else None
        )


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class BookmarkBlock(EmbedBlock):
    pass


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class ImageBlock(FileObject):
    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.image(
            url=self.get_url(),
            caption=self.to_markdown_caption(context))


@dataclass_dict_convert(dict_letter_case=snakecase)
@dataclass
class PdfBlock(FileObject):
    def to_markdown(self, context: MarkdownContext) -> str:
        return MarkdownBuilder.embed(
            url=f'https://docs.google.com/viewer?url={urllib.parse.quote_plus(self.get_url())}&embedded=true',
            caption=self.to_markdown_caption(context) or ' ')


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

    def to_markdown(self, context: MarkdownContext) -> str:
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
            return self.bulleted_list_item.to_markdown(context)
        elif self.type == BlockType.numbered_list_item:
            return self.numbered_list_item.to_markdown(context)
        elif self.type == BlockType.to_do:
            return self.to_do.to_markdown(context)
        elif self.type == BlockType.embed:
            return self.embed.to_markdown(context)
        elif self.type == BlockType.pdf:
            return self.pdf.to_markdown(context)
        elif self.type == BlockType.bookmark:
            return self.bookmark.to_markdown(context)
        elif self.type == BlockType.unsupported:
            return 'Unsupported Block Type!'
        else:
            raise Exception('unsupported! ' + self.type.value)

    def get_part(self) -> Union[ToMarkdownMixin]:
        return getattr(self, self.type.value)

    def set_children(self, children: List['Block']):
        part = self.get_part()
        if isinstance(part, ChildrenMixin):
            part.set_children(children)
        else:
            raise Exception(f'Block {self.type} does not support children')

    def get_children(self) -> List['Block']:
        part = self.get_part()
        if isinstance(part, ChildrenMixin):
            return part.get_children()
        else:
            raise Exception(f'Block {self.type} does not support children')

    def countable(self) -> bool:
        part = self.get_part()
        if isinstance(part, ToMarkdownMixin):
            return self.get_part().countable()
        else:
            return super().countable()
