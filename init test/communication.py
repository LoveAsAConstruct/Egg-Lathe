import serial
import time
from threading import Thread

class SerialCommunication:
    def __init__(self, port="/dev/cu.usbmodem101", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.connection = serial.Serial(self.port, self.baud_rate, timeout=1)
        time.sleep(2)  # Wait for connection to establish

    def send_command(self, command):
        self.connection.write((command + "\n").encode())

    def receive_status(self):
        if self.connection.in_waiting > 0:
            return self.connection.readline().decode().strip()
        return ""

    def request_state(self, update_status_callback):
        def run():
            while True:
                self.send_command("getState")
                time.sleep(0.1)  # Adjust based on how frequently you want to poll the state
                state = self.receive_status()
                if state:
                    update_status_callback(state)
        Thread(target=run, daemon=True).start()
