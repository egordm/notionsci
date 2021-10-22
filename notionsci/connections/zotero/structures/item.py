import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

from dataclass_dict_convert import dataclass_dict_convert
from stringcase import camelcase

from notionsci.connections.zotero.structures import ID, Links, Library, Meta, Entity
from notionsci.utils import serde, Undefinable


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


@serde(camel=True)
@dataclass
class Tag:
    tag: str
    type: Undefinable[int] = None


@serde(camel=True, ignore_unknown=True)
@dataclass
class ItemData(Entity):
    item_type: ItemType
    date_added: dt.datetime
    date_modified: dt.datetime

    parent_item: Undefinable[ID] = None
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
        result.update(result['properties'])
        del result['properties']
        return result

    return wrap


@serde(
    camel=True,
    custom_from_dict_convertors={
        'data': item_from_dict_converter()
    },
    custom_to_dict_convertors={
        'data': item_to_dict_converter()
    },
)
@dataclass
class Item(Entity):
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
