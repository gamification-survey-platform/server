import datetime

from django.forms.fields import DateTimeFormatsIterator


def parse_datetime(value):
    for format in DateTimeFormatsIterator():
        try:
            return datetime.datetime.strptime(value, format)
        except (ValueError, TypeError):
            pass
    raise ValueError('Invalid datetime string')
