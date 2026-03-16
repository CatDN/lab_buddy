import tkinter as tk
import math
import time
import threading

class BuddyEyes:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buddy Alert")
        self.root.configure(bg="black")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)  # always on top


        self.canvas = tk.Canvas(
            self.root, width=400, height=200,
            bg="black", highlightthickness=0
        )
        self.canvas.pack()

        # State: "safe", "warning", "alert"
        self.state = "safe"
        self.blink = False
        self.t = 0  # animation tick

        self.after_id = None
        self._draw()

    def set_state(self, state):
        # Call this from your agent: "safe", "warning", "alert"
        self.state = state

    def _iris_color(self):
        return {"safe": "#00ff88", "warning": "#ffaa00", "alert": "#ff2222"}[self.state]

    def _draw_eye(self, cx, cy, blink):
        r_outer = 55
        r_iris = 30
        r_pupil = 14

        # Idle float animation
        offset_x = math.sin(self.t * 0.03) * 6
        offset_y = math.cos(self.t * 0.02) * 3

        color = self._iris_color()

        # Outer glow ring
        glow = 8
        self.canvas.create_oval(
            cx - r_outer - glow, cy - r_outer - glow,
            cx + r_outer + glow, cy + r_outer + glow,
            fill="", outline=color, width=1
        )

        if blink:
            # Closed eye — just a horizontal line
            self.canvas.create_line(
                cx - r_outer, cy, cx + r_outer, cy,
                fill=color, width=3
            )
        else:
            # White of eye
            self.canvas.create_oval(
                cx - r_outer, cy - r_outer,
                cx + r_outer, cy + r_outer,
                fill="#111111", outline=color, width=2
            )
            # Iris
            self.canvas.create_oval(
                cx - r_iris + offset_x, cy - r_iris + offset_y,
                cx + r_iris + offset_x, cy + r_iris + offset_y,
                fill=color, outline=""
            )
            # Pupil
            self.canvas.create_oval(
                cx - r_pupil + offset_x, cy - r_pupil + offset_y,
                cx + r_pupil + offset_x, cy + r_pupil + offset_y,
                fill="black", outline=""
            )
            # Catchlight
            self.canvas.create_oval(
                cx - 6 + offset_x, cy - 10 + offset_y,
                cx + 2 + offset_x, cy - 4 + offset_y,
                fill="white", outline=""
            )

    def _draw(self):
        self.canvas.delete("all")
        self.t += 1

        # Blink every ~120 ticks
        blinking = (self.t % 120) < 4

        # Alert state — rapid flicker
        if self.state == "alert":
            blinking = (self.t % 10) < 2

        self._draw_eye(110, 100, blinking)
        self._draw_eye(290, 100, blinking)

        self.after_id = self.root.after(30, self._draw)  # ~33fps

    def run(self):
        self.root.mainloop()


# Global instance so main.py can update state
_eyes = None

def start_eyes():
    global _eyes
    _eyes = BuddyEyes()
    _eyes.run()  # blocking — run in a thread

def set_eye_state(state):
    if _eyes:
        _eyes.set_state(state)

def stop_eyes():
    if _eyes:
        _eyes.root.quit()

# test
if __name__ == "__main__":
    import time
    import threading

    def cycle_states():
        time.sleep(2)
        for state in ["safe", "warning", "alert", "safe"]:
            print(f"State: {state}")
            set_eye_state(state)
            time.sleep(3)

    threading.Thread(target=cycle_states, daemon=True).start()
    start_eyes()
    stop_eyes()