# 14/03/2026
##############################################################
# Sources:
# - https://ai.google.dev/gemini-api/docs/audio?_gl=1*1kq0tbd*_up*MQ..*_ga*MTcyMTk3MzM4My4xNzczNDgxODk2*_ga_P1DBVKWT6V*czE3NzM0ODQ2ODAkbzIkZzAkdDE3NzM0ODQ2ODAkajYwJGwwJGgxODc2MzE0MjAw

##############################################################
# for the API key
from dotenv import load_dotenv
import os

# for the agent
from google import genai
from google.genai import types
import json

# for the voice
import pyaudio
import wave
import io

load_dotenv()

# the agent
model =  os.getenv("MODEL")

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
DURATION = int(os.getenv("DURATION"))  # seconds to record

def record_audio():
    p = pyaudio.PyAudio()

    stream = p.open(
        format =pyaudio.paInt16,
        channels= CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Listening...")

    frames= []
    for _ in range(0, int(SAMPLE_RATE/CHUNK * DURATION)):
        frames.append(stream.read(CHUNK))

    stream.stop_stream()
    stream.close()
    p.terminate()

    # write to an in-memory WAV file
    buffer = io.BytesIO()
    wf = wave.open(buffer, "wb")
    
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

    return buffer.getvalue()

def check_voice(client):
    audio_bytes = record_audio()

    response = client.models.generate_content(
        model=model,
        contents = [
                    'Listen to this audio. Does the person sound safe and okay? Consider tone, urgency and what they say. JSON only, no markdown: {"safe": true/false, "reason": "brief explanation"}',
                    types.Part.from_bytes(
                        data = audio_bytes,
                        mime_type = "audio/wav"
                    )
                    ],
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )
        
    )

    result = json.loads(response.text)
    print(f"Voice check: {result}")
    return result

if __name__ == "__main__":

    # check audio recording only first
    # audio_bytes = record_audio()
    # with open("test_recording.wav", "wb") as f:
    #     f.write(audio_bytes)
    # print("Saved to test_recording.wav")

    # check both componens
    check_voice()
    print("checked")

