from dataclasses import dataclass
from typing import Optional, List, Iterator, Union

from notion_client import Client

from notion_research.connections.notion.common import ID, SortObject, QueryFilter, QueryResult, Database, Page, \
    format_query_args
from notion_research.utils import filter_none_dict


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


def iter_items(iter: Iterator[QueryResult]) -> Iterator[Union[Page, Database]]:
    for result in iter:
        yield from result.results


@dataclass
class NotionDatabase(NotionApiMixin, Database):
    def query(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None,
            start_cursor: str = None,
            page_size: int = None
    ) -> QueryResult:
        args = format_query_args(filter=filter, sorts=sorts, start_cursor=start_cursor, page_size=page_size)
        result_raw = self._client().databases.query(self.id, **args)
        result = QueryResult.from_dict(result_raw)
        return result

    def query_all(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None
    ):
        args = dict(filter=filter, sorts=sorts, page_size=100)
        done = False
        while not done:
            result = self.query(**args)
            done = not result.has_more
            args['start_cursor'] = result.next_cursor
            yield result


@dataclass
class NotionClient(NotionApiMixin):
    def database(self, id: ID) -> NotionDatabase:
        return NotionDatabase(client=self.client, id=id)

    def search(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None,
            start_cursor: str = None,
            page_size: int = None
    ) -> QueryResult:
        args = format_query_args(filter=filter, sorts=sorts, start_cursor=start_cursor, page_size=page_size)
        result_raw = self.client.search(**args)
        result = QueryResult.from_dict(result_raw)
        return result

    def search_all(
            self,
            filter: Optional[QueryFilter] = None,
            sorts: Optional[List[SortObject]] = None
    ):
        args = dict(filter=filter if filter else None, sorts=sorts, page_size=100)
        done = False
        while not done:
            result = self.search(**args)
            done = not result.has_more
            args['start_cursor'] = result.next_cursor
            yield result
