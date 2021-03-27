###############################################################################
# Module Imports
###############################################################################

import requests
import logging

###############################################################################
# Global Constants And Variables
###############################################################################

log = logging.getLogger(__name__)

###############################################################################
# Utility Classes
###############################################################################

class InsistentRequest(requests.Session):
    """Make an auto-retrying request that handles connection loss."""

    def __init__(self, max_attempts=10):
        super().__init__()
        self.max_attempts = max_attempts

    def __repr__(self):
        return '{}(max_attempts={})'.format(
            self.__class__.__name__, self.max_attempts)

    def request(self, method, url, **kwargs):
        logged_kwargs = repr(kwargs) if kwargs else ''
        log.debug('%s: %s %s', method, url, logged_kwargs)

        kwargs.setdefault('timeout', 60)
        kwargs.setdefault('allow_redirects', False)
        for _ in range(self.max_attempts):
            try:
                resp = super().request(method=method, url=url, **kwargs)
            except (
                    requests.ConnectionError,
                    requests.Timeout,
                    requests.exceptions.ChunkedEncodingError):
                continue
            return resp
            if 200 <= resp.status_code < 300:
                return resp
            elif 400 <= resp.status_code < 600:
                continue
        raise requests.ConnectionError(
            'Max retries exceeded with url: {}'.format(url))

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

###############################################################################
# Exception Classes
###############################################################################

class NotFoundException(Exception): pass