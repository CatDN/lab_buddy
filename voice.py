# 21/03/2026

import asyncio
import pyaudio
import base64
import os
import threading
from dotenv import load_dotenv
from elevenlabs import AudioFormat, CommitStrategy, ElevenLabs, RealtimeEvents, RealtimeAudioOptions

load_dotenv()

SAMPLE_RATE = 16000
CHUNK = 1600
COMMIT_INTERVAL = 5

latest_transcript = ""
_connection = None
_loop = None

async def _stream():
    global latest_transcript, _connection

    elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    _connection = await elevenlabs.speech_to_text.realtime.connect(
        RealtimeAudioOptions(
            model_id="scribe_v2_realtime",
            audio_format=AudioFormat.PCM_16000,
            sample_rate=SAMPLE_RATE,
            commit_strategy=CommitStrategy.MANUAL,
        )
    )
    print("ElevenLabs connected")

    def on_partial(data):
        global latest_transcript
        text = data.get("text", "")
        if text:
            latest_transcript = text

    def on_committed(data):
        global latest_transcript
        text = data.get("text", "")
        if text:
            latest_transcript = text
            print(f"Committed: {latest_transcript}")

    _connection.on(RealtimeEvents.PARTIAL_TRANSCRIPT, on_partial)
    _connection.on(RealtimeEvents.COMMITTED_TRANSCRIPT, on_committed)
    _connection.on(RealtimeEvents.ERROR, lambda e: print(f"ElevenLabs error: {e}"))
    _connection.on(RealtimeEvents.CLOSE, lambda: print("ElevenLabs connection closed"))

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    last_commit = asyncio.get_event_loop().time()
    is_first = True

    try:
        while True:
            chunk = await asyncio.get_event_loop().run_in_executor(
                None, lambda: stream.read(CHUNK, exception_on_overflow=False)
            )

            payload = {"audio_base_64": base64.b64encode(chunk).decode()}
            if is_first:
                payload["previous_text"] = "Safety monitoring conversation"
                is_first = False

            await _connection.send(payload)

            now = asyncio.get_event_loop().time()
            if now - last_commit >= COMMIT_INTERVAL:
                await _connection.commit()
                last_commit = now

    except asyncio.CancelledError:
        pass
    finally:
        await _connection.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start_voice():
    global _loop
    _loop = asyncio.new_event_loop()
    threading.Thread(target=_run_loop, args=(_loop,), daemon=True).start()
    asyncio.run_coroutine_threadsafe(_stream(), _loop)
    print("Voice streaming started")

def stop_voice():
    global _loop
    if _loop:
        _loop.call_soon_threadsafe(_loop.stop)
    print("Voice streaming stopped")

def check_voice() -> dict:
    """Returns the latest transcript from the continuous ElevenLabs stream."""
    return {"transcript": latest_transcript}

if __name__ == "__main__":
    import time
    start_voice()
    for _ in range(30):
        time.sleep(1)
        print(f"Latest: {latest_transcript}")
    stop_voice()