import html
import re
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict

import pandas as pd


@dataclass
class MarkdownContext:
    mode: str = 'typora'
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
'''.strip() + '\n'

IMAGE_TEMPLATE = '''
<figure>
  <img src="{url}" alt="{alt}" style="width:100%">
  <figcaption>{caption}</figcaption>
</figure>
'''.strip() + '\n'

TOGGLE_TEMPLATE = '''
<details>
    <summary>{title}</summary>
    {content}
</details>
'''.strip() + '\n'

YOUTUBE_TEMPLATE = '''
<figure>
    <iframe 
        width="560" 
        height="315" 
        src="https://www.youtube.com/embed/{url}" 
        title="YouTube video player" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
    </iframe>
  <figcaption>{caption}</figcaption>
</figure>
'''.strip() + '\n'


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
    def video(url, caption=None):
        if 'youtube' in url:
            video_id = re.search(
                r'^.*(youtu.be\/|v\/|embed\/|watch\?|youtube.com\/user\/[^#]*#([^\/]*?\/)*)\??v?=?([^#\&\?]*).*',
                url).group(3)
            return YOUTUBE_TEMPLATE.format(
                url=video_id,
                caption=html.escape(caption if caption else url),
            )
        else:
            return MarkdownBuilder.url(url, f'Video: {caption if caption else url}')

    @staticmethod
    def heading(text, type='paragraph'):
        if type == 'paragraph':
            return f'{text}  '
        elif type == 'h1':
            return f'# {text}'
        elif type == 'h2':
            return f'## {text}'
        elif type == 'h3':
            return f'### {text}'
        elif type == 'h4':
            return f'#### {text}'
        elif type == 'h5':
            return f'##### {text}'
        elif type == 'h6':
            return f'###### {text}'

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

    @staticmethod
    def table(data: pd.DataFrame, alignments: Dict[str, str] = None):
        if alignments:
            for col, align in alignments.items():
                data.style.set_properties(subset=[col], **{'text-align': align})
        return data.to_markdown()


def chain_to_markdown(items: List[ToMarkdownMixin], context: MarkdownContext, sep='', prefix=''):
    result = []
    for item in items:
        if not item.countable():
            context.counter = 1
        result.append(item.to_markdown(context))

    return sep.join(map(lambda x: f'{prefix}{x}', filter(lambda x: x is not None, result))) if items else None
