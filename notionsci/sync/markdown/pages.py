import datetime as dt
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

from notionsci.connections.notion import Page, ID, NotionClient, SortObject, SortDirection, DateValue, Property
from notionsci.sync import Action
from notionsci.sync.structure import Sync, ActionTarget, ActionType
from notionsci.utils import sanitize_filename, MarkdownContext


@dataclass
class MarkdownPage:
    filename: str
    path: Optional[str] = None
    created_at: Optional[dt.datetime] = None
    updated_at: Optional[dt.datetime] = None
    synced_at: Optional[dt.datetime] = None
    deleted: bool = False

    def __post_init__(self):
        # On some filesystems, created at can be greater than modified at
        if self.created_at is not None and self.updated_at is not None:
            upperbound_time = min(self.created_at, self.synced_at) if self.synced_at else self.created_at
            self.updated_at = self.updated_at if self.updated_at >= upperbound_time else upperbound_time

    def get_title(self):
        return self.path.replace('.md', '')


PROPERTY_PATTERN = r'\|\s*{property_name}\s*\|(.*)\|'
SYNCED_AT_PATTERN = PROPERTY_PATTERN.format(property_name='Synced At')


@dataclass
class MarkdownPagesSync(Sync[MarkdownPage, Page]):
    notion: NotionClient
    database_id: ID
    markdown_dir: str

    def fetch_items_a(self) -> Dict[str, MarkdownPage]:
        print('Loading existing Markdown pages')
        path = Path(self.markdown_dir)
        pages = []
        for file in path.glob('**/*.md'):
            if not file.is_file():
                continue

            content = file.read_text()
            synced_at = re.search(SYNCED_AT_PATTERN, content)

            pages.append(MarkdownPage(
                file.name,
                str(file.absolute()),
                created_at=dt.datetime.fromtimestamp(os.path.getctime(file)),
                updated_at=dt.datetime.fromtimestamp(os.path.getmtime(file)),
                synced_at=dt.datetime.fromisoformat(synced_at.group(1).strip()) if synced_at else None,
                deleted='deleted' in file.parts
            ))

        return {page.filename.replace('.md', ''): page for page in pages}

    def fetch_items_b(self) -> Dict[str, Page]:
        print('Loading existing Notion pages')
        return {
            sanitize_filename(page.get_title()): page
            for page in self.notion.database_query_all(
                self.database_id,
                sorts=[SortObject(property='Modified At', direction=SortDirection.descending)],
                filter=None
            )
        }

    def compare(self, a: Optional[MarkdownPage], b: Optional[Page]) -> Action[MarkdownPage, Page]:
        if a is None:  # Doesn't exist in markdown
            return Action.push(ActionTarget.A, a, b)
        if b is None:  # Doesn't exist in notion
            if a.deleted:
                return Action.ignore()
            else:
                return Action.push(ActionTarget.B, a, b)

        if a.deleted:
            return Action.delete(ActionTarget.B, a, b)

        locally_modified = a.synced_at is None or a.updated_at > a.synced_at
        remote_modified = b.get_propery_value('Synced At') is None \
                          or b.get_propery_value('Modified At') > b.get_propery_value('Synced At')
        if locally_modified and remote_modified:
            return Action.merge(a, b)
        elif locally_modified:
            return Action.push(ActionTarget.B, a, b)
        elif remote_modified:
            return Action.push(ActionTarget.A, a, b)

        return Action.ignore()

    def execute_a(self, action: Action[MarkdownPage, Page]):
        if action.action_type == ActionType.PUSH:
            # Load page property
            page = action.b
            self.notion.load_children(page, recursive=True, databases=True)
            path = os.path.join(self.markdown_dir, f'{sanitize_filename(page.get_title())}.md')
            synced_at = dt.datetime.now()

            # Update synced at property
            if page.has_property('Synced At'):
                page.get_property('Synced At').set_raw_value(DateValue.from_date(synced_at))
            else:
                page.extend_properties({
                    'Synced At': Property.as_date(synced_at)
                })

            # TODO: Save to notion

            # Download page to markdown
            content = page.to_markdown(MarkdownContext())
            with open(path, 'w') as f:
                f.write(content)

            # Update file modified at such that it is before synced at
            os.utime(path, (synced_at.timestamp() - 5, synced_at.timestamp() - 5))
            print(f'- [MARKDOWN] Updated: {action.b.get_title()}')
        elif action.action_type == ActionType.PUSH:
            page = action.b
            path = os.path.join(self.markdown_dir, f'{sanitize_filename(page.get_title())}.md')
            os.remove(path)
            print(f'- [MARKDOWN] Deleted: {action.b.get_title()}')
        else:
            return super().execute_a(action)

    def execute_b(self, action: Action[MarkdownPage, Page]):
        if action.action_type == ActionType.PUSH:
            pass
            print(f'- [NOTION] Updated: {action.a.get_title()}')
        elif action.action_type == ActionType.PUSH:
            pass
            print(f'- [NOTION] Deleted: {action.b.get_title()}')
        else:
            return super().execute_a(action)
