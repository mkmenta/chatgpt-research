from pytz import timezone
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin

from flask import request, escape, Request
# from werkzeug import Request
from werkzeug.datastructures import ImmutableMultiDict


class HTTPMethodOverrideMiddleware(object):
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])
    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app, field='_method'):
        self.app = app
        self._regex = re.compile('.*' + field + '=([a-zA-Z]+)(&.*|$)')

    def __call__(self, environ, start_response):
        method = self._regex.match(environ.get('QUERY_STRING', ''))
        if method is not None:
            method = method.group(1).upper()
            if method in self.allowed_methods:
                environ['REQUEST_METHOD'] = method
            if method in self.bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)


class SanitizedRequest(Request):
    """Sanitizes form fields automatically to escape HTML."""

    def __init__(self, environ, populate_request=True, shallow=False):
        super(SanitizedRequest, self).__init__(environ, populate_request, shallow)
        self.unsanitized_form = self.form
        if self.form:
            sanitized_form = {}
            for k, v in self.form.items():
                sanitized_form[k] = escape(v)
            self.form = ImmutableMultiDict(sanitized_form)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def now_mytz():
    rome = timezone('Europe/Rome')
    return datetime.now(tz=rome)
