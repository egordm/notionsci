import re


def is_uuid(value):
    if not value: return False

    value = value.replace('-', '').lower()
    return not not re.match(r'^[0-9a-f]{32}$', value)


def parse_uuid(value):
    if not is_uuid(value):
        raise Exception(f'Could not parse notion uuid from: {value}')

    value = value.replace('-', '').lower()
    return f'{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}'


def parse_uuid_or_url(value):
    try:
        if is_uuid(value):
            return parse_uuid(value)
        else:
            return extract_uuid_from_url(value)
    except Exception:
        raise Exception(f'{value} is neither a valid notion uuid or a notion page url')


def parse_uuid_callback(ctx, param, value):
    return parse_uuid_or_url(value)


def parse_uuid_or_str_callback(ctx, param, value):
    try:
        return parse_uuid_or_url(value)
    except Exception:
        return value


def extract_uuid_from_url(url: str):
    if 'notion.site' in url or 'notion.so' in url:
        return parse_uuid(url.split('?')[0].split('/')[-1].split('-')[-1])
    raise Exception(f'{url} is not recognized as one holding notion content.')
