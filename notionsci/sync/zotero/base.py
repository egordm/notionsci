import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict

from notionsci.connections.notion import Page, ID, NotionClient, SortObject, SortDirection, Parent
from notionsci.connections.zotero import ZoteroClient, Entity
from notionsci.sync.structure import Sync, Action, ActionTarget, B, ActionType, A

PROP_MODIFIED_AT = 'Modified At'
PROP_SYNCED_AT = 'Synced At'
PROP_VERSION = 'Version'


def compare_entity(a: Entity, b: Page, force: bool):
    # modified_remote = b.get_propery_value(PROP_MODIFIED_AT) > b.get_propery_value(PROP_SYNCED_AT)
    if a.version > b.get_propery_value(PROP_VERSION, 0) or force:
        return Action.push(ActionTarget.B, a, b)
    else:
        return Action.ignore()


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
            x.get_propery_value('ID'): x
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
        return compare_entity(a, b, self.force)

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
