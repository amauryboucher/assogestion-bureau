from sqlalchemy import inspect


def format_date_to_database(date):
    date_split = date.split('/')
    date_format = f"{date_split[2]}-{date_split[1]}-{date_split[0]}"
    return date_format

def format_date_to_ouput(date):
    date_split = date.split('-')
    date_format = f"{date_split[2]}-{date_split[1]}-{date_split[0]}"
    return date_format

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}