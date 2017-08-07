import asyncio
from unittest.mock import patch
from functools import wraps
from aioresponses import aioresponses

import pytest
from tests.conftest import mock_response


loop = asyncio.get_event_loop()


@mock_response('auth.json')
def test_auth(m_sab):
    z = loop.run_until_complete(m_sab.auth())
    assert z['auth'] == 'apikey'


@mock_response('version.json')
def test_version(m_sab):
    v = loop.run_until_complete(m_sab.version())
    assert v


@mock_response('queue.json')
def test_queue(m_sab):
    x = loop.run_until_complete(m_sab.queue())
    assert x


@mock_response('history.json')
def test_history(m_sab):
    x = loop.run_until_complete(m_sab.history())
    assert x
