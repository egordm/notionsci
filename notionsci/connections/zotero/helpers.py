import re
from typing import List, Iterable, Dict, Set

from notionsci.connections.zotero.common import ID, Collection, Item


def build_inherency_tree(collections: Iterable[Collection]) -> Dict[ID, Set[ID]]:
    result = {}

    def inherency_tree(collection: Collection, parents: List[ID]):
        if collection.children:
            parents_next = [*parents, collection.key]
            for child in collection.children.values():
                inherency_tree(child, parents_next)

        if collection.key not in result:
            result[collection.key] = set()

        result[collection.key] = result[collection.key].union(parents)

    for c in collections:
        inherency_tree(c, [])

    return result


def generate_citekey(item: Item):
    """
    Generates cite key according to default better bibtex format
    [auth:lower][shorttitle3_3][year]
    :param item:
    :return:
    """
    authors = item.authors.lower().split()
    author = authors[0] if len(authors) > 0 else ''
    shorttitle3_3 = short_title(item.title, 3)
    year = item.year

    return f'{author}{shorttitle3_3}{year}'


def short_title(title: str, l: int = 3):
    pattern = re.compile(r'[^ \w+]')
    title = pattern.sub('', title)
    tokens = title.split()[0:l]
    return ' '.join(tokens).title().replace(' ', '')
