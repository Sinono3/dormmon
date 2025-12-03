import tkinter as tk
import ttkbootstrap as ttk
import serial
import threading

class NoiseAlertPopup:
    def __init__(self):
        self.popup = None

    def show_popup(self, message):
        if self.popup is None:  # Create popup if it does not exist
            self.popup = tk.Toplevel()
            self.popup.title("Noise Alert")
            self.popup.geometry("300x100")
            label = tk.Label(self.popup, text=message, font=("Helvetica", 16), fg='red')
            label.pack(expand=True, padx=20, pady=20)
            self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)  # Handle close event

    def close_popup(self):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None

import random
import time
class NoiseAlertPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.popup = NoiseAlertPopup()
        self.thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.thread.start()

    def simulate_serial_input(self):
        """Simulate serial input for testing the UI."""
        noise_threshold = 22  # Example threshold
        while True:
            # Generate a random sound level to simulate noise levels
            simulated_noise_level = random.randint(0, 100)

            # Determine if the noise level exceeds the threshold
            if simulated_noise_level > noise_threshold:
                message = "ALERT!"
            else:
                message = "No Alert"

            # Simulate reading the message in the noise_alert_page
            self.process_serial_data(message)

            # Wait before generating the next reading
            time.sleep(1)  # Change the duration as needed for testing

    def process_serial_data(self, line):
        """Process incoming simulated serial data."""
        if "ALERT!" in line:
            self.popup.show_popup("Noise Level High!")
        elif "No Alert" in line:
            self.popup.close_popup()


    def read_serial_data(self):
        # self.simulate_serial_input()  # for testing only

        with serial.Serial('/dev/ttyACM0', 9600, timeout=1) as ser:  # Adjust port as needed
            noise_alert_active = False
            while True:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    if "ALERT!" in line and not noise_alert_active:
                        self.popup.show_popup("Noise Level High!")
                        noise_alert_active = True
                    elif "No Alert" in line and noise_alert_active:
                        self.popup.close_popup()
                        noise_alert_active = False
