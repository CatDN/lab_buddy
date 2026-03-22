# 21/03/2026
from dotenv import load_dotenv
import os
import time
import threading
import cv2
from pynput import keyboard


from google import genai
from google.genai import types

from camera import start_camera, stop_camera, check_camera, get_latest_frame
from voice import start_voice, stop_voice, check_voice
from alarm import play_alarm
from email_alert import send_alert_email
from eyes import start_eyes, set_eye_state, stop_eyes
from voice_prompt import speak, stop as stop_voice_prompt
from log_window import start_log_window, stop_log_window


stop_event = threading.Event()

def _on_press(key):
    try:
        if key.char == 'q':  # press q to quit
            print("Kill key pressed — shutting down...")
            stop_event.set()
    except AttributeError:
        pass  # special key, ignore

def start_kill_key():
    listener = keyboard.Listener(on_press=_on_press)
    listener.daemon = True
    listener.start()

load_dotenv()

MODEL          = os.getenv("MODEL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 5))
STILLNESS_SECS = 5
NO_SPEECH_SECS = 5

alert_sent = False

SAFE_KEYWORDS = [
    "fine", "okay", "ok", "good", "yes",
    "all good", "i'm fine", "im fine", "safe",
    "bueno", "bom"
]

DISTRESS_KEYWORDS = [
    "ow", "ouch", "help", "hurt", "pain", "stop",
    "shit", "fuck", "damn", "christ", "jesus", "epa", "tsc",
    "shite", "god", "mau", "ai", "fogo"
]

SYSTEM_PROMPT = """You are a safety assessment agent. You will receive a camera frame 
and a voice transcript. Assess whether the person is safe or in distress.
If you determine the person is in danger or unresponsive, use the send_alert_email 
tool to notify their guardian with a clear explanation.
If it's not possible to ascertain their safety, or the assessment is inconclsive, send
the email anyways. It's better to be cautious.
Always end your response with exactly one of:
STATUS:SAFE, STATUS:WARNING, or STATUS:ALERT"""


def contains_keyword(transcript, keywords):
    t = transcript.lower()
    return any(kw in t for kw in keywords)


def frame_to_bytes(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()


def prompt_voice_check():
    set_eye_state("warning")
    threading.Thread(
        target=speak, args=("Please confirm you are okay",), daemon=True
    ).start()


def send_alert_email_wrapped(reason: str) -> dict:
    """Sends an emergency alert email to the configured guardian.

    Args:
        reason: Brief explanation of why the alert is being sent.
    """
    global alert_sent
    if not alert_sent:
        set_eye_state("alert")
        frame = get_latest_frame()
        send_alert_email(reason, frame=frame)
        alert_sent = True
        print(f"  Alert email sent: {reason}")
        return {"status": "email sent"}
    return {"status": "email already sent"}


def call_gemini(client, camera_result, transcript):
    print("  → Calling Gemini for safety assessment...")

    # build contents — frame + text description
    contents = []
    frame = get_latest_frame()
    if frame is not None:
        contents.append(types.Part.from_bytes(
            data=frame_to_bytes(frame),
            mime_type="image/jpeg"
        ))

    contents.append(types.Part.from_text(text=
        f"Camera: {camera_result.get('description', 'No description')}\n"
        f"Voice transcript: '{transcript}'\n"
        f"Motion detected: {camera_result.get('moving', 'unknown')}\n"
        f"Pose safe: {camera_result.get('pose_safe', 'unknown')}"
    ))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[send_alert_email_wrapped],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    response = client.models.generate_content(
        model=MODEL,
        config=config,
        contents=contents
    )

    # agentic loop — handle tool calls
    while True:
        function_calls = response.function_calls

        if not function_calls:
            text = response.text
            print(f"  Gemini: {text}")
            if "STATUS:ALERT" in text:
                set_eye_state("alert")
                threading.Thread(target=play_alarm, daemon=True).start()
                return "alert"
            elif "STATUS:WARNING" in text:
                set_eye_state("warning")
                return "warning"
            else:
                set_eye_state("safe")
                return "safe"

        tool_response_parts = []
        for fc in function_calls:
            name = fc.name
            args = dict(fc.args) if fc.args else {}
            print(f"  → Calling {name}...")
            if name == "send_alert_email_wrapped":
                result = send_alert_email_wrapped(**args)
            else:
                result = {"error": f"Unknown tool: {name}"}
            print(f"  ← {result}")
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": result}
                )
            )

        # feed tool results back
        contents = contents + [
            types.Part.from_function_response(
                name=fc.name,
                response={"result": {}}
            ) for fc in function_calls
        ] + tool_response_parts

        response = client.models.generate_content(
            model=MODEL,
            config=config,
            contents=contents
        )


def run_check(client):
    global alert_sent

    camera     = check_camera()
    transcript = check_voice().get("transcript", "")
    present    = camera.get("present", False)
    moving     = camera.get("moving", True)
    seconds_still = camera.get("seconds_still", 0)

    print(f"  Camera: present={present} moving={moving} still={seconds_still}s")
    print(f"  Transcript: '{transcript}'")

    # case 1 — person present and moving
    if present and moving:
        if contains_keyword(transcript, DISTRESS_KEYWORDS):
            set_eye_state("warning")
            print("Distress keyword detected — calling Gemini")
            call_gemini(client, camera, transcript)
        else:
            set_eye_state("safe")
            print("Safe — person present and moving")
            alert_sent = False
        return

    # case 2 — no person OR person not moved for STILLNESS_SECS
    if not present or seconds_still >= STILLNESS_SECS:
        set_eye_state("warning")
        reason = "No person in frame" if not present else f"No movement for {seconds_still}s"
        print(f"{reason} — prompting voice check")
        prompt_voice_check()
        time.sleep(NO_SPEECH_SECS)

        # re-read transcript after waiting
        transcript = check_voice().get("transcript", "")
        print(f"  Post-prompt transcript: '{transcript}'")

        if contains_keyword(transcript, SAFE_KEYWORDS):
            print("Voice confirmed safe")
            set_eye_state("safe")
            alert_sent = False
        elif contains_keyword(transcript, DISTRESS_KEYWORDS):
            set_eye_state("warning")
            print("Distress keyword detected — calling Gemini")
            call_gemini(client, camera, transcript)
        else:
            set_eye_state("warning")
            print("No response — calling Gemini")
            call_gemini(client, camera, transcript)


if __name__ == "__main__":
    threading.Thread(target=start_eyes, daemon=True).start()
    threading.Thread(target=start_log_window, daemon=True).start()
    start_camera()
    start_voice()
    start_kill_key()
    time.sleep(1)

    with genai.Client() as client:
        print("Buddy Alert started. Press Q to stop.\n")
        try:
            while not stop_event.is_set():
                print("--- Check ---")
                run_check(client)
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            stop_camera()
            stop_voice()
            stop_voice_prompt()
            stop_eyes()
            stop_log_window()
            print("Shutdown complete.")