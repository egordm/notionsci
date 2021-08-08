from dataclasses import dataclass
from typing import Optional, List, Dict

from pyzotero.zotero import Zotero

from notion_research.connections.notion import NotionNotAttachedException
from notion_research.connections.zotero.common import SearchParameters, SearchPagination, Item, ID


class ZoteroNotAttachedException(Exception):
    pass


@dataclass
class ZoteroApiMixin:
    client: Optional[Zotero] = None

    def attached(self) -> bool:
        return self.client is not None

    def attach(self, client: Zotero):
        self.client = client

    def detach(self):
        self.client = None

    def _client(self):
        if not self.attached():
            raise NotionNotAttachedException()

        return self.client


@dataclass
class ZoteroClient(ZoteroApiMixin):
    def items(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
            **kwargs
    ) -> List[Item]:
        result_raw = self.client.items(
            **(params.to_query() if params else {}),
            **(pagination.to_query() if pagination else {}),
            **kwargs
        )
        return [Item.from_dict(item) for item in result_raw]

    def all_items(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
    ):
        pagination = pagination if pagination else SearchPagination()
        done = False
        while not done:
            result = self.items(
                params,
                pagination
            )

            if len(result) < pagination.limit:
                done = True
            pagination.start = pagination.start + pagination.limit

            yield from result

    def all_items_tree(self) -> List[Item]:
        items: Dict[ID, Item] = {
            item.key: item
            for item in self.all_items()
        }

        known_children = set()
        for child_key, child in items.items():
            if child.data.parent_item and child.data.parent_item in items:
                parent = items[child.data.parent_item]
                if not parent.children:
                    parent.children = {}
                parent.children[child_key] = child
                known_children.add(child_key)

        for k in known_children:
            del items[k]

        return items
