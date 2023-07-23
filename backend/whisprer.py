import diart.operators as dops
import rx.operators as ops
from utils import concat, jsonify_transcription
import traceback
from client import Client
import asyncio
import threading
import logging


class Whisprer:

    def __init__(self):
        self.clients = {}

    def handle_new_chunks(self, sid):
        logging.info("New chunks handler started")
        client = self.clients[sid]
        source = client.get_source()
        while True:
            if not client.audio_chunks.empty():
                current_chunk = client.audio_chunks.get()
                # not a heavy operation but a blocking one at times, shouldn't block the main thread thanks to asyncio
                source.receive_chunk(current_chunk)

    # FULL CREDIT TO JUANMA CORIA FOR THIS DIART IMPLEMENTATION WITH WHISPER (COLOR YOUR CAPTIONS ON MEDIUM)
    async def transcription_thread(self, sid):
        logging.info("Transcription thread started")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.handle_new_chunks, sid)
        logging.info(asyncio.get_running_loop())
        client = self.clients[sid]
        source = client.get_source()
        diarization_pipeline = client.get_diarization_pipeline()
        config = client.get_pipeline_config()
        asr = client.get_transcriber()

        # Split the stream into 2s chunks for transcription
        transcription_duration = 2
        # Apply models in batches for better efficiency
        batch_size = int(transcription_duration // config.step)

        source.stream.pipe(
            dops.rearrange_audio_stream(config.duration, config.step, config.sample_rate),
            ops.buffer_with_count(count=batch_size),
            ops.map(diarization_pipeline),
            ops.map(concat),
            ops.filter(lambda ann_wav: ann_wav[0].get_timeline().duration() > 0),
            ops.starmap(asr),
            ops.map(jsonify_transcription),
            ops.take_while(lambda result: result is not None and len(result) > 0 and not client.is_disconnected())
        ).subscribe(
            on_next=lambda result: asyncio.run(client.send_transcription(result)),
            on_error=lambda _: traceback.print_exc(),
        )

    async def start_stream(self, sid, sio, config):
        if sid not in self.clients.keys():
            transcription_thread = threading.Thread(target=asyncio.run, args=(self.transcription_thread(sid),))
            new_client = Client(sid=sid, socket=sio, transcription_thread=transcription_thread, config=config)
            self.clients[sid] = new_client
            await new_client.start_transcribing()
        else:
            logging.warning("A streaming client tried to initiate another stream")
            await sio.emit("This client is already transcribing")

    async def end_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            await client.stop_transcribing()
            self.clients.pop(sid)

    def disconnect_from_stream(self, sid):
        if sid in self.clients.keys():
            client = self.clients[sid]
            client.handle_disconnection()
            self.clients.pop(sid)
            logging.info("Disconnected client removed")
        else:
            logging.warning("A non-existent client tried to disconnect from the stream.")

    def receive_chunk(self, sid, chunk):
        client = self.clients.get(sid)
        if not client:
            logging.warning("Non-existent client tried to receive chunk.")
            return
        client.audio_chunks.put(chunk)
