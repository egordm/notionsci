from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Any, Iterator, TypeVar, Union

from pyzotero.zotero import Zotero

from notionsci.connections.notion import NotionNotAttachedException
from notionsci.connections.zotero import Entity
from notionsci.connections.zotero.structures import SearchParameters, SearchPagination, Item, ID, Collection
from notionsci.utils import list_from_dict


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
        return list_from_dict(Collection, result_raw)

    def all_collections(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
    ):
        yield from traverse_pagination(
            pagination, lambda pagination: self.collections(params, pagination)
        )

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
        return list_from_dict(Item, result_raw)

    def all_items(
            self,
            params: Optional[SearchParameters] = None,
            pagination: Optional[SearchPagination] = None,
    ):
        yield from traverse_pagination(
            pagination, lambda pagination: self.items(params, pagination)
        )

    def all_items_grouped(self, delete_children: bool = True) -> List[Item]:
        return group_entities(self.all_items(), lambda x: x.data.parent_item, delete_children)

    def all_collections_grouped(self, delete_children: bool = True) -> List[Collection]:
        return group_entities(self.all_collections(), lambda x: x.data.parent_collection, delete_children)


T = TypeVar('T')


def traverse_pagination(
        args: Optional[SearchPagination],
        query_fn: Callable[[SearchPagination], List[T]]
) -> Iterator[T]:
    if not args:
        args = SearchPagination()

    done = False
    while not done:
        result = query_fn(args)
        if len(result) < args.limit:
            done = True
        args.start = args.start + args.limit

        yield from result


def group_entities(
        items: Iterator[Union[Entity, T]],
        parent_key: Callable[[T], ID],
        delete_children: bool = True
):
    results: Dict[ID, T] = {
        x.key: x for x in items
    }

    # Assign items to the right parents
    known_children = set()
    for child_key, child in results.items():
        if not parent_key(child) or parent_key(child) not in results:
            continue

        parent = results[parent_key(child)]
        if not parent.children: parent.children = {}
        parent.children[child_key] = child
        known_children.add(child_key)

    if delete_children:
        for k in known_children:
            del results[k]

    return list(results.values())
