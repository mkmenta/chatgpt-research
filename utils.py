from pytz import timezone
from datetime import datetime
import re
from urllib.parse import urlparse, urljoin

from flask import request, escape, Request
import tiktoken
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


class TokenCounter:
    """Returns the number of tokens used by a list of messages.
    
    Based on: https://platform.openai.com/docs/guides/chat/managing-tokens
    """
    def __init__(self,  model="gpt-3.5-turbo-0301"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def num_tokens_from_string(self, text):
        return len(self.encoding.encode(text))

    def num_tokens_from_messages(self, messages):
        """Returns the number of tokens used by a list of messages.
        
        From: https://platform.openai.com/docs/guides/chat/managing-tokens
        """
        if self.model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += self.num_tokens_from_string(value)
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {self.model}.
            See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
