import html
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


@dataclass
class MarkdownContext:
    depth: int = 0
    counter: int = 1

    def copy(self, **kwargs):
        return MarkdownContext(**{
            **self.__dict__,
            **kwargs
        })


class ToMarkdownMixin:
    @abstractmethod
    def to_markdown(self, context: MarkdownContext) -> str:
        pass

    def countable(self) -> bool:
        return False


EMBED_TEMPLATE = '''
<figure>
  <iframe 
    height='265' 
    title='{caption}' src='{url}' 
    frameborder='no' allowtransparency='true' 
    allowfullscreen='true' style='width: 100%;'></iframe>
  <figcaption>{caption}</figcaption>
</figure>
'''.strip()

IMAGE_TEMPLATE = '''
<figure>
  <img src="{url}" alt="{alt}" style="width:100%">
  <figcaption>{caption}</figcaption>
</figure>
'''.strip()

TOGGLE_TEMPLATE = '''
<details>
    <summary>{title}</summary>
    {content}
</details>
'''.strip()


class MarkdownListType(Enum):
    bullet = 'bullet'
    numeric = 'numeric'


class MarkdownBuilder:
    @staticmethod
    def url(url, alt=None):
        return f'[{alt or url}]({url})'

    @staticmethod
    def equation(equation: str):
        return f'${equation}$'

    @staticmethod
    def image(url, caption=None, alt=None):
        if not caption:
            return f'!{MarkdownBuilder.url(url, alt)}'
        else:
            return IMAGE_TEMPLATE.format(
                url=url,
                caption=html.escape(caption),
                alt=html.escape(alt or caption)
            )

    @staticmethod
    def embed(url, caption=None):
        return EMBED_TEMPLATE.format(
            url=url,
            caption=html.escape(caption if caption else url),
        )

    @staticmethod
    def heading(text, type='paragraph'):
        if type == 'paragraph':
            return text
        elif type == 'h1':
            return f'# {text}'
        elif type == 'h2':
            return f'## {text}'
        elif type == 'h3':
            return f'## {text}'

    @staticmethod
    def list(text, context: MarkdownContext, type: MarkdownListType = MarkdownListType.bullet):
        if type == MarkdownListType.bullet:
            return f'* {text}'
        elif type == MarkdownListType.numeric:
            res = f'{context.counter}. {text}'
            context.counter += 1
            return res

    @staticmethod
    def todo(text, checked: bool):
        return f'- [x] {text}' if checked else f'- [ ] {text}'

    @staticmethod
    def toggle(title, content):
        return TOGGLE_TEMPLATE.format(title=title, content=content)


def chain_to_markdown(items: List[ToMarkdownMixin], context: MarkdownContext, sep='', prefix=''):
    result = []
    for item in items:
        if not item.countable():
            context.counter = 1
        result.append(item.to_markdown(context))

    return sep.join(map(lambda x: f'{prefix}{x}', filter(lambda x: x is not None, result))) if items else None
