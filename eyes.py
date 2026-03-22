import tkinter as tk
import math
import time
import threading

class BuddyEyes:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Buddy Alert")
        self.root.configure(bg="black")

        # get screen dimensions
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # top right quadrant
        win_w = screen_w // 2
        win_h = screen_h // 2
        x = screen_w // 2  # start at halfway across
        y = 0              # top of screen

        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            self.root, width=win_w, height=win_h,
            bg="black", highlightthickness=0
        )
        self.canvas.pack()

        self.state = "safe"
        self.t = 0
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

        w = self.root.winfo_width()
        h = self.root.winfo_height()

        blink_cycle = self.t % 150
        if blink_cycle < 8:
            blink_frac = math.sin(blink_cycle / 8 * math.pi)
        else:
            blink_frac = 0

        if self.state == "alert":
            blink_frac = max(blink_frac, math.sin((self.t % 20) / 20 * math.pi) * 0.6)

        # position eyes at 1/3 and 2/3 across, centred vertically
        self._draw_eye(w // 3,     h // 2, blink_frac)
        self._draw_eye(w // 3 * 2, h // 2, blink_frac)

        self.root.after(30, self._draw)

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