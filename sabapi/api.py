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
        self.__own_client = False
        self._api_key = apikey
        self._output = output
        self._url = url.rstrip('/') + '/sabnzbd/api'

        self._defaults = {'output': output,
                          'apikey': self._api_key}
        self._last_call = ''
        self._config = {} # sabnzbd config.

        if client is None:
            self.__own_client = True
            self._client = httpclient()
        else:
            self._client = client

    def __del__(self):
        # Only close the _client if the
        # sabapi created the ClientSession
        if self.__own_client is True:
            @asyncio.coroutine
            def clean_up():
                yield from self._client.close()
                del self._client
                self._client = None

            l = asyncio.get_event_loop()
            l.run_until_complete(clean_up())

    @asyncio.coroutine
    def _query(self, mode, method='get', timeout=10, **kwargs):
        kw = kwargs.copy()
        kw.update(self._defaults)
        kw['mode'] = mode

        # The api expects 1 or 0 for bool
        clean_kw = {}
        for k, v in kw.items():
            if type(v) == bool:
                v = int(v)
            clean_kw[k] = v

        resp = yield from fetch(self._url, self._client,
                                t=timeout, params=clean_kw)
        self._last_call = resp.url

        if self._output == 'json':
            data = yield from resp.json()
            err = data.get('error')
            if resp.status == 200 and err:
                raise SabnzbdHttpError(err)
            #yield from resp.release()
            return data

        elif self._output == 'xml':
            data = yield from resp.text()
            #return ET.fromstring(data)

        else:
            return (yield from resp.text())

    @asyncio.coroutine
    def reachable(self):
        resp = None
        resp = (yield from self._query('auth'))
        if resp:
            return True
        return False

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
    def auth(self):
        return (yield from self._query('auth'))

    @asyncio.coroutine
    def full_status(self, skip_dashboard=True):

        """Get all status information available from SABnzbd.

           Args:
                skip_dashboard(bool): Skip getting public IPv4 address

        """
        return (yield from self._query('fullstatus', skip_dashboard=skip_dashboard))

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

    @asyncio.coroutine
    def delete_jobs(self, nzo, delete_files=False):
        """Remove a job or all jobs from the queue.
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

    @asyncio.coroutine
    def add_url(self, url, name='', category='*', script='Default', priority=-100, pp=1):
        """Add a nzb via url to sabnzbd

           Args:
                url(str): url to nzb
                name (str, optional): Name of the job, if empty the NZB filename is used.
                                      NOTE If you want to supply a password, it needs to be part
                                      of the name/nzbname or provided inside the NZB, see: RAR with password.

                category(str, optional): * Means default, you can get a list of categories from get_categories
                script(str, optional): Sabnzbd will use the default script for the category, get possible scripts from
                             get_scripts
                priority(int, optional): -100 = Default Priority (of category)
                                         -2 = Paused
                                         -1 = Low Priority
                                         0 = Normal Priority
                                         1 = High Priority
                                         2 = Force
                pp(int, optional):  Post procesing options
                                    -1 = Default (of category)
                                    0 = None
                                    1 = +Repair
                                    2 = +Repair/Unpack
                                    3 = +Repair/Unpack/Delete



        """

        return (yield from self._query('addurl', name=url, nzbname=name,
                                       cat=category, script=script,
                                       priority=priority, pp=pp))

    @asyncio.coroutine
    def add_localfile(self, path, name='', category='*', script='Default', priority=-100, pp=1):
        """Add a local file, sabnzbd must be able to reach the path."""
        return (yield from self._query('addlocalfile', name=path, nzbname=name,
                                       cat=category, script=script,
                                       priority=priority, pp=pp))

    @asyncio.coroutine
    def change_job_category(self, nzo, category):
        """Get the categories from get_cats."""
        return (yield from self._query('change_cat', value=nzo, value2=category))

    @asyncio.coroutine
    def change_job_script(self, nzo, script):
        """Get the script for get_scripts"""
        return (yield from self._query('change_cat', value=nzo, value2=script))

    @asyncio.coroutine
    def change_job_priority(self, nzo, pos):
        return (yield from self._query('queue', name='priority',
                                       value=nzo, value2=pos))

    @asyncio.coroutine
    def change_job_postprocessing(self, nzo, pos):
        return (yield from self._query('change_pts', value=nzo, value2=pos))

    @asyncio.coroutine
    def change_job_name(self, nzo, name, password=None):
        # api?mode=queue&name=rename&value=NZO_ID&value2=NEW_NAME&value3=PASSWORD
        return (yield from self._query('queue', name='rename', value=nzo,
                                       value2=name, password=password))

    @asyncio.coroutine
    def get_files(self, nzo):
        """Get all the files for a job."""
        return (yield from self._query('get_files', value=nzo))

    @asyncio.coroutine
    def remove_job(self, nzo, nzf):
        """Remove a job from the queue

        """
        return (yield from self._query('queue', name='delete', value=nzo,
                                       value2=nzf))

    @asyncio.coroutine
    def delete_history(self, nzo):
        """Delete history

           Args:
                nzo (str, list): a single nzo, a list of nzos, failed or all.

        """
        return (yield from self._query('history', name='delete', value=nzo))

    @asyncio.coroutine
    def retry(self, nzo, password=None):
        if nzo == 'all':
            return (yield from self._query('retry_all'))

        return (yield from self._query('retry', value=nzo, password=password))

    @asyncio.coroutine
    def history(self, start=0, limit=0, category='', search='', failed=False, last_history_update=False):
        return (yield from self._query('history', start=start, limit=limit,
                                       category=category, search=search,
                                       failed_only=failed,
                                       last_history_update=last_history_update))

    @asyncio.coroutine
    def server_stats(self):
        """Return download statistics in bytes, total and per-server."""
        return (yield from self._query('server_stats'))

    @asyncio.coroutine
    def get_config(self, section=None, key=None):
        if section is None and key is None:
            return (yield from self._query('get_config'))
        return (yield from self._query('get_config', section=section, keyword=key))

    @asyncio.coroutine
    def set_config(self, section=None, key=None, value=None):
        return (yield from self._query('set_config', section=section,
                                       keyword=key, value=value))

    @asyncio.coroutine
    def warnings(self):
        return (yield from self._query('warnings'))

    @asyncio.coroutine
    def version(self):
        return (yield from self._query('version'))
