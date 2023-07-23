import logging
from diart import OnlineSpeakerDiarization
from audio_source import StreamingSocketAudioSource
from config import DIARIZATION_PIPELINE_CONFIG, LANGUAGE_MAPPING
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
        model = self.config.get("model", "small")
        language = self.config.get("language", None)
        if language is not None:
            try:
                language_code = LANGUAGE_MAPPING[language.lower()]
            except KeyError:
                logging.warning("Language not supported")
                language_code = None
        else:
            language_code = None
        self.transcriber = WhisperTranscriber(model_name=model, language_code=language_code)

    async def start_transcribing(self):
        self.transcription_thread.start()
        await self.socket.emit("whisperingStarted")

    async def stop_transcribing(self):
        self.transcription_thread.join()
        logging.info("Transcription thread closed")
        await self.socket.emit("whisperingStopped")

    def handle_disconnection(self):
        self.disconnected = True
        self.transcription_thread.join()
        logging.info("Transcription thread closed after disconnection")

    async def send_transcription(self, transcription):
        logging.info("Transcription sent")
        logging.info(transcription)
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
