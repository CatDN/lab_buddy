# 14/03/2026
# for the API key
from dotenv import load_dotenv
import os

# for the agent
from google import genai
from google.genai import types
import json


# for the camera and imaging
import cv2
from PIL import Image

load_dotenv()

# the agent
model =  os.getenv("MODEL")

def capture_frame():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        raise RuntimeError("Could not read from webcam")
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)

def check_camera(client):
    img = capture_frame()
    response = client.models.generate_content(
        model=model,
        contents = [img, 
                    'Is a person visible and do they appear conscious and safe? Reply with JSON only, no markdown: {"present": true/false, "safe": true/false, "reason": "brief explanation"}'
                    ],
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)

        )
    )


    result = json.loads(response.text)
    print(f"Camera check: {result}")

    return result


# capture_frame()
# Test
if __name__ == "__main__":
    check_camera()