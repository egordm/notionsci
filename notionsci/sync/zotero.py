import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, List, TypeVar, Set

import pytz

from notionsci.connections.notion import Page, ID, NotionClient, SortObject, SortDirection, Property, \
    Parent, RelationItem
from notionsci.connections.zotero import Item, ZoteroClient, generate_citekey, Collection, build_inherency_tree
from notionsci.sync.structure import Sync, Action, ActionTarget, B, ActionType, topo_sort
from notionsci.utils import key_by, flatten

A = TypeVar('A')


@dataclass
class ZoteroNotionOneWaySync(Sync[A, Page], ABC):
    notion: NotionClient
    zotero: ZoteroClient
    database_id: ID
    force: bool = False
    last_sync_date: Optional[dt.datetime] = None

    def fetch_items_b(self) -> Dict[str, B]:
        print('Loading existing Notion items')
        return {
            x.get_property('ID').value(): x
            for x in self.notion.database_query_all(
                self.database_id,
                sorts=[SortObject(property='Modified At', direction=SortDirection.descending)],
                filter=None
            )
        }

    def compare(self, a: Optional[A], b: Optional[Page]) -> Action[A, B]:
        if a is None:
            return Action.delete(ActionTarget.B, a, b)
        if b is None:
            return Action.push(ActionTarget.B, a, b)
        if a.updated_at().replace(tzinfo=pytz.utc) > b.get_property('Synced At').value().replace(tzinfo=pytz.utc) \
                or self.force:
            return Action.push(ActionTarget.B, a, b)

        return Action.ignore()

    @abstractmethod
    def collect_props(self, a: A):
        pass

    def execute_b(self, action: Action[A, B]):
        if action.action_type == ActionType.PUSH:
            if not action.b:
                action.b = Page(
                    parent=Parent.database(self.database_id),
                )

            action.b.extend_properties(self.collect_props(action.a))
            action.b = self.notion.page_upsert(action.b)
            print(f'- Updated: {action.b.get_title()}')
        elif action.action_type.DELETE:
            action.b.archived = True
            action.b = self.notion.page_update(action.b)
            print(f'- Deleted: {action.b.get_title()}')


@dataclass
class RefsOneWaySync(ZoteroNotionOneWaySync[Item]):
    collections_id: Optional[ID] = None
    notion_collections: Dict[ID, Page] = field(default_factory=dict)
    zotero_collections: Dict[ID, Collection] = field(default_factory=dict)
    collection_sets: Dict[ID, Set[ID]] = field(default_factory=dict)

    def fetch_items_a(self) -> Dict[str, A]:
        print('Loading existing Zotero items')
        return {
            x.key: x
            for x in self.zotero.all_items_grouped(delete_children=True)
        }

    def preprocess(self, items_a: Dict[str, A], items_b: Dict[str, B], keys: List[str]):
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
            'Tags': Property.as_multi_select([tag.tag for tag in a.data.tags]),
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
            'Synced At': Property.as_date(dt.datetime.now())
        }


@dataclass
class CollectionsOneWaySync(ZoteroNotionOneWaySync[Collection]):
    zotero_notion_ids: Dict[str, str] = field(default_factory=dict)

    def fetch_items_a(self) -> Dict[str, A]:
        print('Loading existing Zotero items')
        return {
            x.key: x
            for x in self.zotero.all_collections_grouped(delete_children=False)
        }

    def preprocess(self, items_a: Dict[str, A], items_b: Dict[str, B], keys: List[str]):
        # Store existing items
        self.zotero_notion_ids = {
            k: items_b[k].id
            for k in items_a.keys() if k in items_b
        }

        # Apply toposort on collections
        keys = topo_sort(
            keys,
            lambda x: items_a[x].children.keys() if x in items_a and items_a[x].children else []
        )

        return super().preprocess(items_a, items_b, keys)

    def collect_props(self, a: A):
        return {
            'ID': Property.as_rich_text(a.key),
            'Name': Property.as_title(a.title),
            'Parent': Property.as_relation(
                [RelationItem(self.zotero_notion_ids[a.data.parent_collection])]
                if a.data.parent_collection else []
            ),
            'Synced At': Property.as_date(dt.datetime.now())
        }

    def execute_b(self, action: Action[A, B]):
        super().execute_b(action)

        if action.action_type == ActionType.PUSH:
            self.zotero_notion_ids[action.a.key] = action.b.id
