from dataclasses import dataclass
from typing import Optional, List, Iterator, Dict, Callable, Any, Union

from notion_client import Client

from notionsci.connections.notion.common import ID, SortObject, QueryFilter, QueryResult, Database, Page, \
    format_query_args, ContentObject, PropertyType
from notionsci.utils import strip_none_field


class NotionNotAttachedException(Exception):
    pass


@dataclass
class NotionApiMixin:
    client: Optional[Client] = None

    def attached(self) -> bool:
        return self.client is not None

    def attach(self, client: Client):
        self.client = client

    def detach(self):
        self.client = None

    def _client(self):
        if not self.attached():
            raise NotionNotAttachedException()

        return self.client


def traverse_pagination(args: dict, query_fn: Callable[[Dict], Any]) -> Iterator[Any]:
    done = False
    while not done:
        result = query_fn(**args)
        done = not result.has_more
        args['start_cursor'] = result.next_cursor
        yield from result.results


READONLY_PROPS = {
    PropertyType.last_edited_time, PropertyType.last_edited_by,
    PropertyType.created_time, PropertyType.created_by
}


def strip_readonly_props(obj: ContentObject):
    keys = [k for k, v in obj.properties.items() if v.type in READONLY_PROPS]
    for k in keys:
        del obj.properties[k]
    return obj


@dataclass
class NotionClient(NotionApiMixin):
    def page_get(self, id: ID) -> Page:
        result = self.client.pages.retrieve(id)
        return Page.from_dict(result)

    def page_update(self, page: Page) -> Page:
        args = strip_none_field(strip_readonly_props(page).to_dict())
        result = self.client.pages.update(page.id, **args)
        return Page.from_dict(result)

    def page_create(self, page: Page) -> Page:
        args = strip_none_field(strip_readonly_props(page).to_dict())
        result = self.client.pages.create(**args)
        return Page.from_dict(result)

    def page_upsert(self, page: Page) -> Page:
        return self.page_update(page) if page.id else self.page_create(page)

    def database_get(self, id: ID) -> Database:
        result = self.client.databases.retrieve(id)
        return Database.from_dict(result)

    def database_create(self, database: Database) -> Database:
        args = strip_none_field(strip_readonly_props(database).to_dict())
        result = self.client.databases.create(**args)
        return Database.from_dict(result)

    def database_query(
            self,
            id: ID,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None,
            start_cursor: str = None,
            page_size: int = None
    ) -> QueryResult:
        args = format_query_args(filter=filter, sorts=sorts, start_cursor=start_cursor, page_size=page_size)
        result_raw = self._client().databases.query(id, **args)
        return QueryResult.from_dict(result_raw)

    def database_query_all(
            self,
            id: ID,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None
    ) -> Iterator[Page]:
        return traverse_pagination(
            args=dict(filter=filter if filter else None, sorts=sorts, page_size=100),
            query_fn=lambda **args: self.database_query(id, **args)
        )

    def search(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None,
            start_cursor: str = None,
            page_size: int = None
    ) -> QueryResult:
        args = format_query_args(filter=filter, sorts=sorts, start_cursor=start_cursor, page_size=page_size)
        result_raw = self.client.search(**args)
        return QueryResult.from_dict(result_raw)

    def search_all(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None
    ) -> Iterator[Union[Page, Database]]:
        return traverse_pagination(
            args=dict(filter=filter if filter else None, sorts=sorts, page_size=100),
            query_fn=lambda **args: self.search(**args)
        )
