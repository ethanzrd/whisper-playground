from aiohttp import web
import socketio
from whisprer import Whisprer

sio = socketio.AsyncServer(cors_allowed_origins=[])
app = web.Application()
sio.attach(app)

whisprer = Whisprer()


@sio.on("connect")
def handle_connect(sid, environ):
    print("Client connected")


@sio.on("disconnect")
def handle_disconnect(sid):
    whisprer.disconnect_from_stream(sid)
    print("Client disconnected")


@sio.on("startWhispering")
async def handle_stream_start(sid, config):
    print(config)
    await whisprer.start_stream(sid=sid, sio=sio, config=config)
    print("Stream started")


@sio.on("stopWhispering")
async def handle_stream_end(sid):
    await whisprer.end_stream(sid)
    print("Stream ended")


@sio.on("audioChunk")
def handle_chunk(sid, chunk):
    print("chunk arrived in server")
    whisprer.receive_chunk(sid, chunk)


if __name__ == "__main__":
    web.run_app(app, port=8000)
