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
        self.alert_widget = None

    def show_popup(self, message, duration=3000):
        if self.alert_widget is not None:
            return

        self.alert_widget = tk.Label(
            self.parent,
            text=message,
            bg="#ff4444",
            fg="white",
            font=("Helvetica", 24, "bold"),
            padx=15,
            pady=10
        )

        # Top center
        self.alert_widget.place(relx=0.5, rely=0.05, anchor="n")

        self.parent.after(duration, self.close_popup)

    def close_popup(self):
        if self.alert_widget is not None:
            self.alert_widget.destroy()
            self.alert_widget = None


class NoiseAlertPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.popup = NoiseAlertPopup(self.parent)

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
        if "ALERT!" in line:
            self.parent.after(0, lambda: self.popup.show_popup("🚨 Noise Level High!"))
        else:
            self.parent.after(0, self.popup.close_popup)

    # ----------------------------
    # MAIN SERIAL READER
    # ----------------------------
    def read_serial_data(self):
        SERIAL_PORT = '/dev/ttyACM0'

        try:
            ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
            print(">> Using REAL SENSOR")

            noise_alert_active = False

            while True:
                if ser.in_waiting:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()

                    if "ALERT!" in line and not noise_alert_active:
                        self.process_serial_data("ALERT!")
                        noise_alert_active = True

                    elif "No Alert" in line and noise_alert_active:
                        self.process_serial_data("No Alert")
                        noise_alert_active = False

        except Exception:
            # Fallback to simulation
            print(">> Sensor not found. Entering SIMULATION MODE.")
            self.simulate_serial_input()
