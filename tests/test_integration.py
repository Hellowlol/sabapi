import asyncio

loop = asyncio.get_event_loop()

def test_auth(sab):
    t = loop.run_until_complete(sab.auth())
    print('t', t)

def test_warnings(sab):
    t = loop.run_until_complete(sab.warnings())
    assert 'warnings' in t

def test_server_stats(sab):
    t = loop.run_until_complete(sab.server_stats())
    assert 'week' in t
