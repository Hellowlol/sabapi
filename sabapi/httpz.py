import asyncio
import logging

import aiohttp
from async_timeout import timeout

LOG = logging.getLogger(__name__)


@asyncio.coroutine
def fetch(url, session, params, method='GET', t=10):
    with timeout(t):
        resp = yield from session.request(method, url, params=params)
        try:
            return resp
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            LOG.exception(err)




def httpclient(session=None, connector=None):
    if session is None:
        session = aiohttp.ClientSession(connector=connector, loop=asyncio.get_event_loop())

    return session
