import asyncio
from unittest.mock import patch
from functools import wraps
from aioresponses import aioresponses

import pytest
from tests.conftest import mock_response


loop = asyncio.get_event_loop()


@mock_response('http://10.0.0.97:8085/sabnzbd/api', 'auth.json')
def test(mocked_sab):
    z = loop.run_until_complete(mocked_sab().auth())
    print('z', z)

@mock_response('auth.json')
def test2(m_sab):
    pass
