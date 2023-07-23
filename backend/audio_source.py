from diart.sources import AudioSource
from config import SAMPLE_RATE
from diart.utils import decode_audio


class StreamingSocketAudioSource(AudioSource):
    def __init__(self, sid):
        self.sample_rate = SAMPLE_RATE
        super().__init__(uri=sid, sample_rate=self.sample_rate)

    def receive_chunk(self, chunk):
        print("about to put chunk in stream")
        self.stream.on_next(decode_audio(chunk))
        print("chunk put in stream")
