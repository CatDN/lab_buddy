
# 21/03/2026
import os
import threading
import sounddevice as sd
import soundfile as sf
import io
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings

load_dotenv()

_lock = threading.Lock()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def speak(text):
    with _lock:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",  #
            model_id="eleven_v3",       #
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
            ),
            output_format="mp3_44100_128",
        )

        # collect audio bytes from generator
        audio_bytes = b"".join(audio)

        # play via sounddevice without saving to disk
        buf = io.BytesIO(audio_bytes)
        data, samplerate = sf.read(buf)
        sd.play(data, samplerate)
        sd.wait()

def stop():
    sd.stop()

if __name__ == "__main__":
    speak("[authoritative] [shouting] Please confirm you are okay!")
    stop()