import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set

from notionsci.connections.notion import Page, ID, SortObject, SortDirection, Property, \
    RelationItem, PropertyDef
from notionsci.connections.zotero import Item, generate_citekey, Collection, build_inherency_tree
from notionsci.sync.structure import B, A
from notionsci.sync.zotero.base import ZoteroNotionOneWaySync, PROP_SYNCED_AT, PROP_VERSION
from notionsci.utils import key_by, flatten

SCHEMA = {
    'ID': PropertyDef.as_rich_text(),
    'Type': PropertyDef.as_select(),
    'Cite Key': PropertyDef.as_title(),
    'Title': PropertyDef.as_rich_text(),
    'Authors': PropertyDef.as_rich_text(),
    'Publication Date': PropertyDef.as_rich_text(),
    'Abstract': PropertyDef.as_rich_text(),
    'URL': PropertyDef.as_url(),
    'Publication': PropertyDef.as_rich_text(),
    'Tags': PropertyDef.as_multi_select(),
    'Special Tags': PropertyDef.as_multi_select(),
    'Collections': PropertyDef.as_multi_select(),
    PROP_SYNCED_AT: PropertyDef.as_date(),
    PROP_VERSION: PropertyDef.as_date(),
}


@dataclass
class RefsOneWaySync(ZoteroNotionOneWaySync[Item]):
    collections_id: Optional[ID] = None
    notion_collections: Dict[ID, Page] = field(default_factory=dict)
    zotero_collections: Dict[ID, Collection] = field(default_factory=dict)
    collection_sets: Dict[ID, Set[ID]] = field(default_factory=dict)
    special_tags_regex: str = None

    def fetch_items_a(self) -> Dict[str, A]:
        print('Loading existing Zotero items')
        return {
            x.key: x
            for x in self.zotero.all_items_grouped(delete_children=True)
        }

    def preprocess(self, items_a: Dict[str, A], items_b: Dict[str, B], keys: List[str]):
        db = self.notion.database_get(self.database_id)
        self.notion.ensure_database_schema(SCHEMA, db)

        if self.collections_id:
            print('Loading existing Notion collections')
            self.notion_collections = {
                x.get_property('ID').value(): x
                for x in self.notion.database_query_all(
                    self.collections_id,
                    sorts=[SortObject(property='Modified At', direction=SortDirection.descending)],
                    filter=None
                )
            }

        print('Loading existing Zotero collections')
        self.zotero_collections = key_by(self.zotero.all_collections_grouped(delete_children=False), 'key')
        self.collection_sets = build_inherency_tree(self.zotero_collections.values())

        return super().preprocess(items_a, items_b, keys)

    def is_special_tag(self, tag: str) -> bool:
        return self.special_tags_regex is not None and re.match(self.special_tags_regex, tag) is not None

    def collect_props(self, a: A):
        item_collections = set(flatten(
            [self.collection_sets.get(col_key, []) for col_key in a.data.collections]
            + [a.data.collections or []]
        ))

        return {
            'ID': Property.as_rich_text(a.key),
            'Type': Property.as_select(a.data.item_type.value),
            'Cite Key': Property.as_title(generate_citekey(a)),
            'Title': Property.as_rich_text(a.title),
            'Authors': Property.as_rich_text(a.authors),
            'Publication Date': Property.as_rich_text(a.date),
            'Abstract': Property.as_rich_text(a.data.abstract),
            'URL': Property.as_url(a.data.url),
            'Publication': Property.as_rich_text(a.data.publication),
            'Tags': Property.as_multi_select(
                [tag.tag for tag in a.data.tags if not self.is_special_tag(tag.tag)]
            ),
            'Special Tags': Property.as_multi_select(
                [tag.tag for tag in a.data.tags if self.is_special_tag(tag.tag)]
            ),
            'Collections': Property.as_multi_select([
                self.zotero_collections[col_key].title
                for col_key in item_collections
                if col_key in self.zotero_collections
            ]),
            'Collection Refs': Property.as_relation([
                RelationItem(self.notion_collections[k].id)
                for k in (a.data.collections or [])
                if k in self.notion_collections
            ]),
            PROP_SYNCED_AT: Property.as_date(dt.datetime.now()),
            PROP_VERSION: Property.as_number(a.version)
        }
