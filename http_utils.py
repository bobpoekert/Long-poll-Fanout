import email.utils as eut
try:
    from urllib2 import parse_http_list as _parse_list_header
except ImportError: # pragma: no cover
    from urllib.request import parse_http_list as _parse_list_header
import datetime

def parse_http_date(date):
    parsed = eut.parsedate(date)
    if not parsed:
        raise ValueError
    return datetime.datetime(*parsed[:6])

def datetime_to_epoch(dt):
    return time.mktime(dt.timetuple())

def parse_dict_header(header):
    return dict(e.split('=') for e in header.split(', '))

def http_date_to_epoch(date):
    return datetime_to_epoch(parse_http_date(date))

# following functions yanked from Werkzeug
# https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/http.py

def unquote_header_value(value, is_filename=False):
    r"""Unquotes a header value.  (Reversal of :func:`quote_header_value`).
    This does not use the real unquoting but what browsers are actually
    using for quoting.

    .. versionadded:: 0.5

    :param value: the header value to unquote.
    """
    if value and value[0] == value[-1] == '"':
        # this is not the real unquoting, but fixing this so that the
        # RFC is met will result in bugs with internet explorer and
        # probably some other browsers as well.  IE for example is
        # uploading files with "C:\foo\bar.txt" as filename
        value = value[1:-1]

        # if this is a filename and the starting characters look like
        # a UNC path, then just return the value without quotes.  Using the
        # replace sequence below on a UNC path has the effect of turning
        # the leading double slash into a single slash and then
        # _fix_ie_filename() doesn't work correctly.  See #458.
        if not is_filename or value[:2] != '\\\\':
            return value.replace('\\\\', '\\').replace('\\"', '"')
    return value

def parse_dict_header(value, cls=dict):
    """Parse lists of key, value pairs as described by RFC 2068 Section 2 and
    convert them into a python dict (or any other mapping object created from
    the type with a dict like interface provided by the `cls` arugment):

    >>> d = parse_dict_header('foo="is a fish", bar="as well"')
    >>> type(d) is dict
    True
    >>> sorted(d.items())
    [('bar', 'as well'), ('foo', 'is a fish')]

    If there is no value for a key it will be `None`:

    >>> parse_dict_header('key_without_value')
    {'key_without_value': None}

    To create a header from the :class:`dict` again, use the
    :func:`dump_header` function.

    .. versionchanged:: 0.9
       Added support for `cls` argument.

    :param value: a string with a dict header.
    :param cls: callable to use for storage of parsed results.
    :return: an instance of `cls`
    """
    result = cls()
    for item in _parse_list_header(value):
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        if value[:1] == value[-1:] == '"':
            value = unquote_header_value(value[1:-1])
        result[name] = value
    return result

# end Werkzeug functions

def parse_cache_control(header):
    cc = parse_dict_header(header)
    val = cc.get('max-age') or cc.get('min-fresh') or cc.get('max-stale')
    if val:
        return datetime.timedelta(seconds=int(val))
    else:
        return None
