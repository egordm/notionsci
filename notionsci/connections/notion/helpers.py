def parse_uuid(value):
    value = value.replace('-', '')
    return f'{value[:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:]}'


def parse_uuid_callback(ctx, param, value):
    return parse_uuid(value)
