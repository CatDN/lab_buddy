# 14/03/2026
import subprocess

def speak(text):
    subprocess.run([
        "powershell", "-Command",
        f"""
        $voice = New-Object -ComObject SAPI.SpVoice
        $voice.Speak("{text}")
        """
    ])



if __name__ == "__main__":
    speak("Please confirm you are okay")


