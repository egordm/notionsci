import re


def is_uuid(value):
    if not value: return False

    value = value.replace('-', '').lower()
    return not not re.match(r'[0-9a-f]{32}', value)


def parse_uuid(value):
    if not is_uuid(value):
        raise Exception(f'Could not parse notion uuid from: {value}')

    value = value.replace('-', '').lower()
    return f'{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}'


def parse_uuid_callback(ctx, param, value):
    return parse_uuid(value)


def parse_uuid_or_str_callback(ctx, param, value):
    return parse_uuid(value) if is_uuid(value) else value
