import sys, os
import pathlib
import websockets, asyncio, ssl

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

async def handler(ws, path):
    try:
        while True:
            data = await ws.recv()
            print(f"WS Server ({ws.path}) sent '{data}'")
            await ws.send(data)
    except websockets.exceptions.ConnectionClosedOK as e:
        print("Client closed", e)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    # create ssl context for websocket secure
    ssl_context = None
    if len(sys.argv) == 2 and sys.argv[1].lower() == "secure":
        normalize_path = lambda path: path.replace("\\", "/").replace("/", os.path.sep)
        ssl_file_path = normalize_path(os.path.join(pathlib.Path(__file__).resolve().parent.parent, "preferences/local.pem"))
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(ssl_file_path)
    # start websocket server
    ws_server = websockets.serve(handler, "127.0.0.1", 1609, ssl=ssl_context)
    asyncio.get_event_loop().run_until_complete(ws_server)
    asyncio.get_event_loop().run_forever()
