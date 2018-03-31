from threading import Thread
import sounddevice as sd
import soundfile as sf


class AudioRecorder(Thread):
    def __init__(self, duration):
        Thread.__init__(self)

        self.duration = duration
        self.samplerate = 44100
        self.channels = 1
        self.output_file = "tmp/record.wav"

    def run(self):
        record = sd.rec(
            int(self.duration * self.samplerate),
            samplerate=self.samplerate,
            channels=self.channels
        )

        sf.write(self.output_file, record, self.samplerate)
        sd.play(record, self.samplerate)
