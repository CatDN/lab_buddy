# 21/03/2026

import tkinter as tk
import sys
import threading

class LogWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buddy Alert — Log")
        self.root.configure(bg="black")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        win_w = screen_w // 2
        win_h = screen_h // 2
        x = screen_w // 2   # right half
        y = screen_h // 2   # bottom half

        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # text widget with scrollbar
        self.text = tk.Text(
            self.root,
            bg="black",
            fg="#00ff88",
            font=("Courier New", 11),
            state=tk.DISABLED,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        # colour tags for different message types
        self.text.tag_config("safe",    foreground="#00ff88")
        self.text.tag_config("warning", foreground="#ffaa00")
        self.text.tag_config("alert",   foreground="#ff2222")
        self.text.tag_config("info",    foreground="#aaaaaa")
        self.text.tag_config("gemini",  foreground="#66aaff")

        # redirect stdout to this window
        sys.stdout = self

    def write(self, message):
        if message.strip() == "":
            return
        self.root.after(0, self._append, message)

    def flush(self):
        pass

    def _append(self, message):
        self.text.configure(state=tk.NORMAL)

        # pick tag based on message content
        msg_lower = message.lower()
        if "alert" in msg_lower:
            tag = "alert"
        elif "warning" in msg_lower or "distress" in msg_lower or "still" in msg_lower:
            tag = "warning"
        elif "safe" in msg_lower or "confirmed" in msg_lower:
            tag = "safe"
        elif "gemini" in msg_lower:
            tag = "gemini"
        else:
            tag = "info"

        self.text.insert(tk.END, message + "\n", tag)
        self.text.configure(state=tk.DISABLED)
        self.text.see(tk.END)  # auto scroll to bottom

    def run(self):
        self.root.mainloop()


_log = None

def start_log_window():
    global _log
    _log = LogWindow()
    _log.run()

def stop_log_window():
    if _log:
        sys.stdout = sys.__stdout__  # restore original stdout
        _log.root.quit()

if __name__ == "__main__":
    import time

    def test_logs():
        time.sleep(1)
        print("System starting up...")
        time.sleep(1)
        print("Safe — person present and moving")
        time.sleep(1)
        print("No movement for 6s — prompting voice check")
        time.sleep(1)
        print("Distress keyword detected — calling Gemini")
        time.sleep(1)
        print("Gemini: Person appears unresponsive STATUS:ALERT")
        time.sleep(1)
        print("Alert email sent: Person slumped in chair")
        time.sleep(1)
        print("Voice confirmed safe")

    threading.Thread(target=test_logs, daemon=True).start()
    start_log_window()