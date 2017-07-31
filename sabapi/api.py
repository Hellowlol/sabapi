import asyncio
import logging

import aiohttp
import async_timeout

from .exceptions import SabnzbdHttpError
from .httpz import fetch, httpclient

LOG = logging.getLogger(__name__)


class Sabnzbd(object):

    def __init__(self, url, apikey='', client=None, output='json'):
        """
        Args:
            url(str): ex http://ip:port
            apikey(str): 1234
            client(aiohttp.ClientSession): Roll your own client for more advance usage.
            output(str): default json. We also allow other but the
                         response is only parsed for json.
        """
        self._api_key = apikey
        self._client = client or httpclient
        self._output = output
        self._url = url.rstrip('/') + '/sabnzbd/api'

        self._defaults = {'output': output,
                          'apikey': self._api_key
                        }
        self._config = {} # sabnzbd config.

    @asyncio.coroutine
    def _query(self, mode, method='get', rtype=None, timeout=10, **kwargs):  # TODO handle rtype. just check the reponse rturn True false.
        kw = kwargs.copy()
        kw.update(self._defaults)
        kw['mode'] = mode
        resp = yield from fetch(self._url, self._client,
                                t=timeout, params=kw)

        if self._output == 'json':
            data = yield from resp.json()
            err = data.get('error')
            if resp.status == 200 and err:
                raise SabnzbHttpError(err)
            return data

        elif self._output == 'xml':
            data = yield from resp.text()
            return ET.fromstring(data)

        else:
            return (yield from resp.text())

    @asyncio.coroutine
    def reachable(self):
        return (yield from self._query('auth'))

    @asyncio.coroutine
    def queue(self, **kwargs):
        return (yield from self._query('queue', **kwargs))

    @asyncio.coroutine
    def pause(self, time=None):
        """Pause Sabnzbd indefinently or for time in min."""
        if time:
            return (yield from self._query('config', name='set_pause',
                                           value=time))
        return (yield from self._query('pause'))

    @asyncio.coroutine
    def config(self, **kwargs):
        return (yield from self._query('config', **kwargs))

    @asyncio.coroutine
    def speedlimit(self, value=0):
        """Args:
                value (int, string): Percentage of line speed or
                                     a set speed if KMB is in the string

        """
        return (yield from self.config(name='speedlimit', value=value))

    @asyncio.coroutine
    def resume(self):
        return (yield from self._query('resume'))

    @asyncio.coroutine
    def auth(self): # response need to be handled
        return (yield from self._query('auth'))

    @asyncio.coroutine
    def full_status(self):
        return (yield from self._query('full_status'))

    @asyncio.coroutine
    def pause_postprocessing(self):
        return (yield from self._query('pause_pp'))

    @asyncio.coroutine
    def resume_postprocessing(self):
        return (yield from self._query('resume_pp'))

    @asyncio.coroutine
    def scan_rss(self):
        return (yield from self._query('rss_now'))

    @asyncio.coroutine
    def scan_watchfolder(self):
        return (yield from self._query('watched_now'))

    @asyncio.coroutine
    def reset_quota(self):
        return (yield from self._query('reset_quota'))

    @asyncio.coroutine
    def reset_apikey(self):
        return (yield from self.config(name='set_apikey'))

    @asyncio.coroutine
    def reset_nzbkey(self):
        return (yield from self.config(name='set_nzbkey'))

    @asyncio.coroutine
    def pause_jobs(self, nzo):
        """Args:
                nzo (str, list):
        """
        #mode=queue&name=resume&value=NZO_ID
        return (yield from self.queue(name='pause', value=nzo))

    @asyncio.coroutine
    def resume_jobs(self, nzo):
        return (yield from self.queue(name='resume', value=nzo))

    # api?mode=queue&name=delete&value=all&del_files=1

    @asyncio.coroutine
    def delete_jobs(self, nzo, delete_files=False):
        """Remove all jobs from the queue, or only the ones matching search.
           Returns nzb_id of the jobs removed

           Args:
                nzo (str, list): if nzo is all all jobs will be deleted.
                delete_files (bool): Delete files


        """

        return (yield from self.queue(name='delete', value=nzo,
                                      del_files=int(delete_files)))

    @asyncio.coroutine
    def purge_queue(self, search=None, delete_files=False):
        """Remove all jobs from the queue, or only the ones matching search.
           Returns nzb_id of the jobs removed

           Args:
                nzo (str, list): if nzo is all all jobs will be deleted.
                delete_files (bool): Delete files
        """

        return (yield from self.queue(name='purge',
                                      del_files=int(delete_files),
                                      search=search))

    @asyncio.coroutine
    def move_job(self, first, second):
        """Move a job in a que to a location or switch places between to nzos.

           Args:
                first (str): nzo
                second (str, int): Position or the nzo to swap with.
        """
        return (yield from self._query('switch', value=first, value2=second))





        #mode=config name=set_nzbkey

# https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary





"""
from collections import defaultdict

class AttributeDict(defaultdict):
    def __init__(self):
        super(AttributeDict, self).__init__(AttributeDict)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

"""
