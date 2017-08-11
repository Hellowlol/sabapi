import asyncio

loop = asyncio.get_event_loop()

def _test_auth(sab):
    t = loop.run_until_complete(sab.auth())

def _test_warnings(sab):
    t = loop.run_until_complete(sab.warnings())
    assert 'warnings' in t

def _test_server_stats(sab):
    t = loop.run_until_complete(sab.server_stats())
    assert 'week' in t
