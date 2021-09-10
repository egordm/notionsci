from abc import abstractmethod
from typing import Any


class ToMarkdownMixin:
    @abstractmethod
    def to_markdown(self, context: Any) -> str:
        pass