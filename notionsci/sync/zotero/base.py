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


def twoway_compare_entity(a: Optional[Entity], b: Optional[Page], force: bool) -> Action[Entity, Page]:
    if a is None:
        return Action.delete(ActionTarget.B, a, b)
    if b is None:
        return Action.push(ActionTarget.B, a, b)

    a_changed = a.version > b.get_propery_value(PROP_VERSION, 0)
    b_changed = b.get_propery_value('Synced At') is None \
                or b.get_propery_value('Modified At') > b.get_propery_value('Synced At')

    if force:
        return Action.push(ActionTarget.B, a, b)

    if a_changed and b_changed:
        return Action.merge(a, b)
    elif a_changed:
        return Action.push(ActionTarget.B, a, b)
    elif b_changed:
        return Action.push(ActionTarget.A, a, b)
    else:
        return Action.ignore()


def oneway_compare_entity(a: Optional[Entity], b: Optional[Page], force: bool) -> Action[Entity, Page]:
    if a is None:
        return Action.delete(ActionTarget.B, a, b)
    if b is None:
        return Action.push(ActionTarget.B, a, b)

    a_changed = a.version > b.get_propery_value(PROP_VERSION, 0)
    if a_changed or force:
        return Action.push(ActionTarget.B, a, b)
    else:
        return Action.ignore()


@dataclass
class ZoteroNotionSync(Sync[A, Page], ABC):
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
            print(f'-[Notion] Updated: {action.b.get_title()}')
        elif action.action_type.DELETE:
            action.b.archived = True
            action.b = self.notion.page_update(action.b)
            print(f'-[Notion] Deleted: {action.b.get_title()}')
