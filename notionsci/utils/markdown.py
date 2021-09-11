import html
from abc import abstractmethod
from typing import Any


class ToMarkdownMixin:
    @abstractmethod
    def to_markdown(self, context: Any) -> str:
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
'''

IMAGE_TEMPLATE = '''
<figure>
  <img src="{url}" alt="{alt}" style="width:100%">
  <figcaption>{caption}</figcaption>
</figure>
'''


class Markdown:
    @staticmethod
    def build_url(url, alt=None):
        return f'[{alt or url}]({url})'

    @staticmethod
    def build_image(url, caption=None, alt=None):
        if not caption:
            return f'!{Markdown.build_url(url, alt)}'
        else:
            return IMAGE_TEMPLATE.format(
                url=url,
                caption=html.escape(caption),
                alt=html.escape(alt or caption)
            )

    @staticmethod
    def build_embed(url, caption=None):
        return EMBED_TEMPLATE.format(
            url=url,
            caption=html.escape(caption if caption else url),
        )
