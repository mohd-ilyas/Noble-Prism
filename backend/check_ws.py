import asyncio
import json
from urllib.request import urlopen

print('HTTP probe:')
try:
    with urlopen('http://127.0.0.1:8000/commerce/providers', timeout=5) as r:
        providers = json.loads(r.read().decode())
        print('PROVIDERS_COUNT', len(providers))
        print('FIRST', providers[0])
except Exception as exc:
    print('PROVIDERS_ERROR', exc)

print('\nWebSocket probe:')
try:
    import websockets

    async def run():
        uri = 'ws://127.0.0.1:8000/commerce/ws'
        async with websockets.connect(uri) as ws:
            msg1 = await ws.recv()
            print('WS1', msg1)
            msg2 = await ws.recv()
            print('WS2', msg2)

    asyncio.run(run())
except Exception as exc:
    print('WS_ERROR', exc)
