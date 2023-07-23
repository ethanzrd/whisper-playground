from diart import OnlineSpeakerDiarization
from audio_source import StreamingSocketAudioSource
from config import DIARIZATION_PIPELINE_CONFIG, NON_SPECIFIC_MODELS
from whisper_transcriber import WhisperTranscriber
import asyncio
from queue import Queue


class Client:

    def __init__(self, sid, socket, transcription_thread, config):
        self.diarization_pipeline = OnlineSpeakerDiarization(DIARIZATION_PIPELINE_CONFIG)
        self.pipeline_config = DIARIZATION_PIPELINE_CONFIG
        self.transcriber = None
        self.config = config
        self.source = StreamingSocketAudioSource(sid)
        self.socket = socket
        self.transcription_thread = transcription_thread
        self.audio_chunks = Queue()
        self.disconnected = False

        self.initialize_transcriber()

    def initialize_transcriber(self):
        print("started")
        model = self.config.get("model", "small")
        self.transcriber = WhisperTranscriber(model=model)

    async def start_transcribing(self):
        self.transcription_thread.start()
        await self.socket.emit("whisperingStarted")

    async def stop_transcribing(self):
        self.transcription_thread.join()  # TODO: CONSIDER ADDING AWAIT - RECOMMENDED BY CHATGPT
        print("Transcription thread closed")
        await self.socket.emit("whisperingStopped")

    def handle_disconnection(self):
        self.disconnected = True
        self.transcription_thread.join()
        print("Transcription thread closed after disconnection")

    async def send_transcription(self, transcription):
        print("Transcription sent")
        print(transcription)
        await self.socket.emit("transcriptionDataAvailable", transcription)

    def receive_chunk(self, chunk):
        self.source.receive_chunk(chunk)

    def get_source(self):
        return self.source

    def get_diarization_pipeline(self):
        return self.diarization_pipeline

    def get_pipeline_config(self):
        return self.pipeline_config

    def get_transcriber(self):
        return self.transcriber

    def is_disconnected(self):
        return self.disconnected
