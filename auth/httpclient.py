"""
    web.py httpclient
    ~~~~~~~~~~~~~~~~

    HTTP client to support `tornado.auth` on web.py.

    :copyright: 2010 by tipfy.org and s-anand.net
    :license: Apache License Version 2.0. See LICENSE.txt for more details.
"""
import functools
import logging
import httplib2
from webpyauth import RequestRedirect

browser = httplib2.Http()

class HttpResponseError(object):
    """A dummy response used when urlfetch raises an exception."""
    code = 404
    body = '404 Not Found'
    error = 'Error 404'


class AsyncHTTPClient(object):
    """An blocking HTTP client that uses urllib."""
    def fetch(self, url, callback, **kwargs):
        if callback is None:
            return None

        try:
            status, content = browser.request(url, **kwargs)
            code = status.status
            setattr(status, 'error', (code < 200 or code >= 300) and code or None)
            setattr(status, 'body', content)
            try:
                return callback(status)
            except RequestRedirect, e:
                raise e
            except Exception, e:
                logging.error("Exception during callback", exc_info=True)
        except RequestRedirect, e:
            raise e
        except Exception, e:
            result = HttpResponseError()
