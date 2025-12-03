import tkinter as tk
import ttkbootstrap as ttk
import serial
import threading
import random
import time
import os

class NoiseAlertPopup:
    def __init__(self, parent):
        self.parent = parent
        self.canvas = None

    def show_popup(self, message, duration=2000):
        if self.canvas is not None:
            return

        root = self.parent.winfo_toplevel()

        w = root.winfo_width()
        h = root.winfo_height()

        self.canvas = tk.Canvas(root, highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, width=w, height=h)

        # Draw a red rectangle covering the screen
        self.canvas.create_rectangle(0, 0, w, h, fill="#aa1111", outline="")

        # Draw centered text (Canvas text is guaranteed to render)
        self.canvas.create_text(
            w // 2,
            h // 2,
            text=message,
            fill="white",
            font=("Helvetica", 32, "bold"),
        )

        root.after(duration, self.close_popup)

    def close_popup(self):
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None            
            
class NoiseAlertPage(ttk.Frame):
    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.popup = NoiseAlertPopup(self.controller)

        self.thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.thread.start()

    # ----------------------------
    # SIMULATION MODE
    # ----------------------------
    def simulate_serial_input(self):
        noise_threshold = 22
        while True:
            level = random.randint(0, 100)
            message = "ALERT!" if level > noise_threshold else "No Alert"
            self.process_serial_data(message)
            time.sleep(1)

    # ----------------------------
    # PROCESS LINES IN UI THREAD
    # ----------------------------
    def process_serial_data(self, line):
        show_alert = ("ALERT!" in line) and self.controller.night_mode
        if show_alert:
            self.controller.after(0, lambda: self.popup.show_popup("🚨 Loud!"))
        else:
            self.controller.after(0, self.popup.close_popup)

    # ----------------------------
    # MAIN SERIAL READER
    # ----------------------------
    def read_serial_data(self):
        SERIAL_PORT = '/dev/ttyACM0'

        try:
            ser = serial.Serial(SERIAL_PORT, 9600, timeout=0.01)
            print(">> Using REAL SENSOR")

            noise_alert_active = False

            while True:
                if ser.in_waiting:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()

                    if "ALERT!" in line and not noise_alert_active:
                        print("ALERT")
                        self.process_serial_data("ALERT!")
                        noise_alert_active = True

                    elif "No Alert" in line and noise_alert_active:
                        self.process_serial_data("No Alert")
                        noise_alert_active = False
                # else:
                #     time.sleep(0.001)

        except Exception:
            # Fallback to simulation
            print(">> Sensor not found. Entering SIMULATION MODE.")
            self.simulate_serial_input()
            pass
