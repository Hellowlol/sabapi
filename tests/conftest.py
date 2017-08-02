import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sabapi import Sabnzbd

import pytest

def client():
    pass


@pytest.fixture
def sab():
    return Sabnzbd(os.environ.get('sabnzbd_url', ''), os.environ.get('sabnzbd_apikey', ''))
