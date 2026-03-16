# 14/03/2026
from dotenv import load_dotenv
import os

import time
import threading
from google import genai
from google.genai import types

from camera import check_camera
from voice import check_voice
from alarm import play_alarm, play_chime
from email_alert import send_alert_email

from eyes import start_eyes, set_eye_state, stop_eyes
from voice_prompt import speak


load_dotenv()
model =  os.getenv("MODEL")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))

SYSTEM_PROMPT = """You are a safety monitoring agent. Every cycle you must:
1. Always check the camera first.
2. If the camera result is uncertain OR unsafe OR if no person is present, flag STATUS:WARNING  AND also check voice.
3. If both checks fail, flag STATUS:ALERT AND play the alarm AND send an alert email explaining why.
4. If everything is fine, report that all is well and safe.
Be decisive. Always use at least the camera tool each cycle.
Always end your final response with exactly one of these words on its own line:
STATUS:SAFE, STATUS:WARNING, or STATUS:ALERT"""

def check_camera_wrapped() -> dict:
    """Captures a webcam frame and returns whether a person is visible and appears safe."""
    result = check_camera(client)
    if result.get("present") and result.get("safe"):
        threading.Thread(target=play_chime, daemon=True).start()
    return result

def check_voice_wrapped() -> dict:
    """Records audio and determines if the person sounds safe based on tone and words."""
    set_eye_state("warning")
    threading.Thread(target=speak, args=("Please confirm you are okay",), daemon=True).start()

    return check_voice(client)

def play_alarm_wrapped() -> dict:
    """Plays a loud alarm sound on this computer."""
    threading.Thread(target=play_alarm, daemon=True).start()
    return {"status": "alarm started"}

def send_alert_email_wrapped(reason: str) -> dict:
    """Sends an emergency alert email to the configured guardian.

    Args:
        reason: Brief explanation of why the alert is being sent.
    """
    set_eye_state("alert")
    send_alert_email(reason)
    return {"status": "email sent"}

def dispatch_tool(function_call):
    name = function_call.name
    args = dict(function_call.args) if function_call.args else {}


    tool_map = {
        "check_camera_wrapped": check_camera_wrapped,
        "check_voice_wrapped": check_voice_wrapped,
        "play_alarm_wrapped": play_alarm_wrapped,
        "send_alert_email_wrapped": send_alert_email_wrapped,
    }

    if name in tool_map:
        print(f"  → Calling {name}...")
        result = tool_map[name](**args)
        print(f"  ← {result}")
        return result
    else:
        return {"error": f"Unknown tool: {name}"}

def run_agent_cycle(chat):
    response = chat.send_message("Run your safety check now.")

    while True:
        function_calls = response.function_calls

        if not function_calls:
            text = response.text
            if "STATUS:ALERT" in text:
                set_eye_state("alert")
            elif "STATUS:WARNING" in text:
                set_eye_state("warning")
            else:
                set_eye_state("safe")
            print(f"Agent: {text}")
            break

        tool_response_parts = []
        for fc in function_calls:
            result = dispatch_tool(fc)
            tool_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": result}
                )
            )

        response = chat.send_message(tool_response_parts)




if __name__ == "__main__":
    # start the eyes
    threading.Thread(target=start_eyes, daemon=True).start()
    time.sleep(0.5)

    with genai.Client() as client:
        chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[check_camera_wrapped, check_voice_wrapped, play_alarm_wrapped, send_alert_email_wrapped],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)

            ))
        try:
            while True:
                print("--- New cycle ---")
                run_agent_cycle(chat)
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            stop_eyes()