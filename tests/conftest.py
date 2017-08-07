import os
import json
import sys
from functools import wraps

import pytest
from aioresponses import aioresponses

RESPONSES = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')), 'responses')
# Make sure the tests work even if the package isnt installed.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sabapi import Sabnzbd


MOCK_URL = 'http://m:8080'
MOCK_API_KEY = '12345'


def mock_response(*deco_args, **deco_kw):
    """Simple decorator that match again the json file.
       Omit the url simpler matching.
    """
    def rd(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with aioresponses() as resp:
                data = {}
                url = None
                fp = os.path.join(RESPONSES, deco_args[1] if len(deco_args) > 1 else deco_args[0])
                with open(fp, 'r') as ff:
                    data = json.loads(ff.read())
                    # incase this was created from the tool
                    if data.get('url') and data.get('response'):
                        data = data['response']
                        url = data.get('url')

                if not url and not deco_args[0].startswith('http'):
                    url = MOCK_URL + '/sabnzbd/api'
                elif not url:
                    url = deco_args[0]

                resp.add(url, payload=data)

                return func(*args, **kwargs)

        return wrapper

    return rd


@pytest.fixture
def sab():
    return Sabnzbd(os.environ.get('sabnzbd_url', ''), os.environ.get('sabnzbd_apikey', ''))


@pytest.fixture()
def m_sab():
    yield Sabnzbd(MOCK_URL, MOCK_API_KEY)
