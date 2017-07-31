import asyncio

loop = asyncio.get_event_loop()

def test_auth(sab):
    t = loop.run_until_complete(sab.auth())
    print('t', t)

