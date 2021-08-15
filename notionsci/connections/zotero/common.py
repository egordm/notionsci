import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

from notionsci.utils import filter_none_dict

ID = str


class LibraryType(Enum):
    group = 'group'
    user = 'user'


Links = Dict
User = Dict


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Library:
    id: int
    type: LibraryType
    name: str
    links: Links


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Meta:
    created_by_user: Optional[User] = None
    parsed_date: Optional[str] = None
    creator_summary: Optional[str] = None
    num_items: Optional[int] = None
    num_collections: Optional[int] = None
    num_children: Optional[int] = None


class ItemType(Enum):
    artwork = 'artwork'
    attachment = 'attachment'
    audioRecording = 'audioRecording'
    bill = 'bill'
    blogPost = 'blogPost'
    book = 'book'
    bookSection = 'bookSection'
    case = 'case'
    computerProgram = 'computerProgram'
    conferencePaper = 'conferencePaper'
    dictionaryEntry = 'dictionaryEntry'
    document = 'document'
    email = 'email'
    encyclopediaArticle = 'encyclopediaArticle'
    film = 'film'
    forumPost = 'forumPost'
    hearing = 'hearing'
    instantMessage = 'instantMessage'
    interview = 'interview'
    journalArticle = 'journalArticle'
    letter = 'letter'
    magazineArticle = 'magazineArticle'
    manuscript = 'manuscript'
    map = 'map'
    newspaperArticle = 'newspaperArticle'
    note = 'note'
    patent = 'patent'
    podcast = 'podcast'
    presentation = 'presentation'
    radioBroadcast = 'radioBroadcast'
    report = 'report'
    statute = 'statute'
    thesis = 'thesis'
    tvBroadcast = 'tvBroadcast'
    videoRecording = 'videoRecording'
    webpage = 'webpage'


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Tag:
    tag: str
    type: Optional[int] = None


def ignore_unknown(field):
    pass


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    on_unknown_field=ignore_unknown
)
@dataclass
class ItemData:
    key: ID
    version: int
    item_type: ItemType
    date_added: dt.datetime
    date_modified: dt.datetime

    parent_item: Optional[ID] = None
    tags: Optional[List[Tag]] = None
    collections: Optional[List[ID]] = None
    relations: Optional[Dict] = None
    properties: Optional[Dict[str, Any]] = None

    def get(self, property: str, default=None):
        return self.properties[property] if property in self.properties else default

    @property
    def title(self):
        if 'title' in self.properties:
            return self.properties['title']
        else:
            if self.item_type == ItemType.note:
                return self.properties['note']
            raise Exception('Title not found')

    @property
    def authors(self):
        if 'creators' in self.properties:
            creators = list(map(lambda x: x['lastName'], self.properties['creators']))
            if len(creators) == 1:
                return creators[0]
            elif len(creators) == 2:
                return ' and '.join(creators)
            elif len(creators) > 2:
                return f'{creators[0]} et al.'
        return ''

    @property
    def date(self):
        return self.get('date', '')

    @property
    def abstract(self):
        return self.get('abstractNote', '')

    @property
    def url(self):
        return self.get('url', None)

    @property
    def publication(self):
        return self.get('publicationTitle', '')


def item_from_dict_converter():
    def wrap(val: dict):
        unknown_fields = []

        def on_unknown_field(field: str):
            unknown_fields.append(field)

        result: ItemData = ItemData.from_dict(val, on_unknown_field_override=on_unknown_field)
        result.properties = {
            field: val[field]
            for field in unknown_fields
        }

        return result

    return wrap


def item_to_dict_converter():
    def wrap(val: ItemData):
        result = ItemData.to_dict(val)
        return result

    return wrap


@dataclass_dict_convert(
    dict_letter_case=camelcase,
    custom_from_dict_convertors={
        'data': item_from_dict_converter()
    },
    custom_to_dict_convertors={
        'data': item_to_dict_converter()
    },
)
@dataclass
class Item:
    key: ID
    version: int
    library: Library
    links: Links
    meta: Meta
    data: ItemData

    children: Optional[Dict[ID, ItemData]] = None

    @property
    def title(self):
        return self.data.title

    @property
    def authors(self):
        return self.meta.creator_summary if self.meta.creator_summary else self.data.authors

    @property
    def date(self):
        return self.meta.parsed_date if self.meta.parsed_date else self.data.date

    @property
    def year(self):
        return self.meta.parsed_date.split('-')[0] if self.meta.parsed_date else ''

    def updated_at(self) -> dt.datetime:
        return self.data.date_modified


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class CollectionData:
    key: ID
    version: int
    name: str
    parent_collection: Optional[ID] = None
    relations: Optional[Dict] = None

    @property
    def title(self):
        return self.name


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class Collection:
    key: ID
    version: int
    library: Library
    links: Links
    meta: Meta
    data: CollectionData

    children: Optional[Dict[ID, CollectionData]] = None
    items: Optional[Dict[ID, ItemData]] = None

    @property
    def title(self):
        return self.data.title

    def updated_at(self) -> dt.datetime:
        return dt.datetime.now()


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class SearchParameters:
    item_key: Optional[List[ID]] = None
    item_type: Optional[str] = None
    q: Optional[str] = None
    since: Optional[int] = None
    tag: Optional[str] = None

    include_trashed: Optional[int] = None

    def to_query(self):
        if isinstance(self.item_key, list):
            self.item_key = ','.join(self.item_key)

        return filter_none_dict(self.to_dict())


class Direction(Enum):
    asc = 'asc'
    desc = 'desc'


@dataclass_dict_convert(dict_letter_case=camelcase)
@dataclass
class SearchPagination:
    sort: Optional[str] = None
    direction: Optional[Direction] = None
    limit: int = 100
    start: int = 0

    def to_query(self):
        return filter_none_dict(self.to_dict())
