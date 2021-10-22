import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from notionsci.connections.notion import Property, \
    RelationItem
from notionsci.connections.zotero import Collection
from notionsci.sync.structure import Action, B, ActionType, topo_sort, A
from notionsci.sync.zotero.base import ZoteroNotionSync, PROP_VERSION, PROP_SYNCED_AT, oneway_compare_entity


@dataclass
class CollectionsSync(ZoteroNotionSync[Collection]):
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

    def compare(self, a: Optional[A], b: Optional[B]) -> Action[A, B]:
        return oneway_compare_entity(a, b, force=self.force)

    def collect_props(self, a: A):
        return {
            'ID': Property.as_rich_text(a.key),
            'Name': Property.as_title(a.title),
            'Parent': Property.as_relation(
                [RelationItem(self.zotero_notion_ids[a.data.parent_collection])]
                if a.data.parent_collection else []
            ),
            PROP_SYNCED_AT: Property.as_date(dt.datetime.now()),
            PROP_VERSION: Property.as_number(a.version)
        }

    def execute_b(self, action: Action[A, B]):
        super().execute_b(action)

        if action.action_type == ActionType.PUSH:
            self.zotero_notion_ids[action.a.key] = action.b.id
