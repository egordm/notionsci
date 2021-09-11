import html
from abc import abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class MarkdownContext:
    pass


class ToMarkdownMixin:
    @abstractmethod
    def to_markdown(self, context: MarkdownContext) -> str:
        pass


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
    def list(text, type='bullet'):
        if type == 'bullet':
            return f'* {text}'
        elif type == 'numeric':
            return f'1. {text}'

    @staticmethod
    def todo(text, checked: bool):
        return f'- [x] {text}' if checked else f'- [ ] {text}'


def chain_to_markdown(items: List[ToMarkdownMixin], context: MarkdownContext, sep=''):
    return sep.join(filter(
        lambda x: x is not None,
        [t.to_markdown(context) for t in items]
    )) if items else None