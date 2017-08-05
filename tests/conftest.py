import os
import json
import sys
from unittest.mock import patch

from functools import partial, wraps

# FIXME
RESPONSES = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')), 'responses')
print(RESPONSES)
# Make sure the tests even if the package isnt installed.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aioresponses import aioresponses

from sabapi import Sabnzbd
from tests.http_utils import mock_aiohttp_client

import pytest

MOCK_URL = 'http://m:8080'
MOCK_API_KEY = '12345'




def mock_response(*deco_args, **deco_kw):
    def rd(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with aioresponses() as resp:
                data = {}
                fp = os.path.join(RESPONSES, deco_args[1] if len(deco_args) > 1 else deco_args[0])
                with open(fp, 'r') as ff:
                    data = ff.read()

                if not deco_args[0].startwith('http'):
                    url = MOCK_URL
                else:
                    url = deco_args[0]

                resp.add(url, payload=json.loads(data))
                return func(*args, **kwargs)

        return wrapper

    return rd



@pytest.fixture
def sab():
    return Sabnzbd(os.environ.get('sabnzbd_url', ''), os.environ.get('sabnzbd_apikey', ''))

@pytest.fixture
def mocked_sab():
    return partial(Sabnzbd, os.environ.get('sabnzbd_url', ''),
                  os.environ.get('sabnzbd_apikey', ''))

@pytest.fixture()
def m_sab():
    return Sabnzbd(MOCK_URL, MOCK_API_KEY)
