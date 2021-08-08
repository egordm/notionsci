from dataclasses import dataclass
from typing import Optional, List, Dict

from pyzotero.zotero import Zotero

from notionsci.connections.notion import NotionNotAttachedException
from notionsci.connections.zotero.common import SearchParameters, SearchPagination, Item, ID, Collection


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
    def collections(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
            **kwargs
    ) -> List[Item]:
        result_raw = self.client.collections(
            **(params.to_query() if params else {}),
            **(pagination.to_query() if pagination else {}),
            **kwargs
        )
        return [Collection.from_dict(item) for item in result_raw]

    def all_collections(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
    ):
        pagination = pagination if pagination else SearchPagination()
        done = False
        while not done:
            result = self.collections(
                params,
                pagination
            )

            if len(result) < pagination.limit:
                done = True
            pagination.start = pagination.start + pagination.limit

            yield from result

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

    def all_items_grouped(self, delete_children: bool = True) -> List[Item]:
        items: Dict[ID, Item] = {
            x.key: x
            for x in self.all_items()
        }

        # Assign items to the right parents
        known_children = set()
        for child_key, child in items.items():
            if not child.data.parent_item:
                continue

            if child.data.parent_item in items:
                parent = items[child.data.parent_item]
                if not parent.children: parent.children = {}
                parent.children[child_key] = child
                known_children.add(child_key)

        if delete_children:
            for k in known_children:
                del items[k]

        return list(items.values())

    def all_collections_grouped(self, delete_children: bool = True) -> List[Collection]:
        collections: Dict[ID, Collection] = {
            x.key: x
            for x in self.all_collections()
        }

        # Assign collections to the right parents
        known_children = set()
        for child_key, child in collections.items():
            if not child.data.parent_collection:
                continue

            if child.data.parent_collection in collections:
                parent = collections[child.data.parent_collection]
                if not parent.children: parent.children = {}
                parent.children[child_key] = child
                known_children.add(child_key)

        if delete_children:
            for k in known_children:
                del collections[k]

        return list(collections.values())
