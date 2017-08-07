import asyncio
from sabapi import Sabnzbd
import os
import json

@asyncio.coroutine
def writer(sab):
    methods = [k for k in dir(sab) if not k.startswith('_')]
    for method in methods:
        try:
            data = yield from getattr(sab, method)()
            if data:
                with open('new_%s.json' % method, 'w') as f:
                    d = {'url': str(sab._last_call),
                         'response': data}

                    json.dump(d, f, sort_keys=True, indent=4)
        except Exception as e:
            print(e, method)


if __name__ == '__main__':
    import argparse
    import asyncio

    loop = asyncio.get_event_loop()
    parser = parser = argparse.ArgumentParser(description='Create new responses from sabnzbd')

    parser.add_argument('-u', '--url', default=False, metavar='keyword',
                        required=False, help='url to sabnzbd')

    parser.add_argument('-a', '--apikey', default=False, metavar='keyword',
                        required=False, help='url to sabnzbd')

    #parser.add_argument('-s', default=False, help='sanitize apikeys etc')

    parser = parser.parse_args()


    sab = Sabnzbd(parser.url or os.environ.get('sabnzbd_url', ''),
                  parser.apikey or os.environ.get('sabnzbd_apikey', ''))

    async def gogo():
        await writer(sab)

    loop.run_until_complete(gogo())


