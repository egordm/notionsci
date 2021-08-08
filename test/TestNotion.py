import unittest

from notion_research.connections.notion.common import QueryResult


class TestNotion(unittest.TestCase):
    def test_parse_items(self):
        data = {'object': 'list', 'results': [
            {'object': 'page', 'id': '32fafc43-1b48-4f05-98e2-4b532abed7ba', 'created_time': '2021-08-08T11:02:00.000Z',
             'last_edited_time': '2021-08-08T11:02:00.000Z',
             'parent': {'type': 'database_id', 'database_id': 'dde52ce1-e694-464e-9294-7c77fa99ac37'},
             'archived': False, 'properties': {'Abstract': {'id': 'BOFs', 'type': 'rich_text', 'rich_text': []},
                                               'Id': {'id': 'Dqe>', 'type': 'rich_text', 'rich_text': []},
                                               'xx': {'id': 'Muvs', 'type': 'people', 'people': []},
                                               'Date': {'id': '[UZf', 'type': 'rich_text', 'rich_text': []},
                                               'Test': {'id': 'fBsq', 'type': 'checkbox', 'checkbox': False},
                                               'Authors': {'id': '~ovq', 'type': 'multi_select', 'multi_select': []},
                                               'Title': {'id': 'title', 'type': 'title', 'title': []}},
             'url': 'https://www.notion.so/32fafc431b484f0598e24b532abed7ba'},
            {'object': 'page', 'id': 'a209ed8e-7b88-4128-bdb5-2f4d3555921b', 'created_time': '2021-08-08T11:02:00.000Z',
             'last_edited_time': '2021-08-08T11:02:00.000Z',
             'parent': {'type': 'database_id', 'database_id': 'dde52ce1-e694-464e-9294-7c77fa99ac37'},
             'archived': False, 'properties': {'Abstract': {'id': 'BOFs', 'type': 'rich_text', 'rich_text': []},
                                               'Id': {'id': 'Dqe>', 'type': 'rich_text', 'rich_text': []},
                                               'xx': {'id': 'Muvs', 'type': 'people', 'people': []},
                                               'Date': {'id': '[UZf', 'type': 'rich_text', 'rich_text': []},
                                               'Test': {'id': 'fBsq', 'type': 'checkbox', 'checkbox': False},
                                               'Authors': {'id': '~ovq', 'type': 'multi_select', 'multi_select': []},
                                               'Title': {'id': 'title', 'type': 'title', 'title': []}},
             'url': 'https://www.notion.so/a209ed8e7b884128bdb52f4d3555921b'},
            {'object': 'page', 'id': '5beaf7fc-e6b3-4c19-b656-391551e29d6d', 'created_time': '2021-08-08T11:02:00.000Z',
             'last_edited_time': '2021-08-08T13:20:00.000Z',
             'parent': {'type': 'database_id', 'database_id': 'dde52ce1-e694-464e-9294-7c77fa99ac37'},
             'archived': False, 'properties': {'Abstract': {'id': 'BOFs', 'type': 'rich_text', 'rich_text': [
                {'type': 'text', 'text': {'content': 'dfsdfsdfsdf', 'link': None},
                 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False,
                                 'code': False, 'color': 'default'}, 'plain_text': 'dfsdfsdfsdf', 'href': None}]},
                                               'Id': {'id': 'Dqe>', 'type': 'rich_text', 'rich_text': [
                                                   {'type': 'text', 'text': {'content': 'abc', 'link': None},
                                                    'annotations': {'bold': False, 'italic': False,
                                                                    'strikethrough': False, 'underline': False,
                                                                    'code': False, 'color': 'default'},
                                                    'plain_text': 'abc', 'href': None}]},
                                               'xx': {'id': 'Muvs', 'type': 'people', 'people': [
                                                   {'object': 'user', 'id': 'f50f071c-d26d-4ccd-938a-81a7ce54d19a',
                                                    'name': 'Egor Dmitriev', 'avatar_url': None, 'type': 'person',
                                                    'person': {'email': 'egordmitriev2@gmail.com'}}]},
                                               'Date': {'id': '[UZf', 'type': 'rich_text', 'rich_text': []},
                                               'Test': {'id': 'fBsq', 'type': 'checkbox', 'checkbox': False},
                                               'uu': {'id': 'l~Dy', 'type': 'email', 'email': 'hh'},
                                               'Authors': {'id': '~ovq', 'type': 'multi_select', 'multi_select': [
                                                   {'id': 'ba94ff86-3737-4a82-8b20-bd44baf5ccd2', 'name': 'World',
                                                    'color': 'purple'}]}, 'Title': {'id': 'title', 'type': 'title',
                                                                                    'title': [{'type': 'text', 'text': {
                                                                                        'content': 'Hello',
                                                                                        'link': None}, 'annotations': {
                                                                                        'bold': False, 'italic': False,
                                                                                        'strikethrough': False,
                                                                                        'underline': False,
                                                                                        'code': False,
                                                                                        'color': 'default'},
                                                                                               'plain_text': 'Hello',
                                                                                               'href': None}]}},
             'url': 'https://www.notion.so/Hello-5beaf7fce6b34c19b656391551e29d6d'}], 'next_cursor': None,
                'has_more': False}

        result = QueryResult.from_dict(data)
        u = 0


if __name__ == '__main__':
    unittest.main()
