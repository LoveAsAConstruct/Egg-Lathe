import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
PORT = '/dev/cu.usbmodem101'  # Change this to your Serial port
BAUD_RATE = 9600
TIMEOUT = 2  # Timeout for serial read in seconds
DATA_RECORDING_INTERVAL = 0.1  # Time interval to check the serial port in seconds

# Initialize serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)

# Data storage
times = []
data = []
last_activity_time = time.time()

def record_serial_data():
    global last_activity_time
    while True:
        if ser.in_waiting > 0:
            reading = ser.readline().decode().strip()
            if reading:
                print(f"Received: {reading}")
                current_time = time.time()
                times.append(current_time)
                data.append(float(reading))  # Assuming numeric data
                last_activity_time = current_time
        else:
            current_time = time.time()
            if current_time - last_activity_time > DATA_RECORDING_INTERVAL * 20:  # Adjust as per requirement for "inactivity"
                break  # Break the loop if no activity
        time.sleep(DATA_RECORDING_INTERVAL)

record_serial_data()
# Function to split data based on inactivity period
def split_data(times, data, inactivity_threshold):
    segments = []
    current_segment = []

    for i in range(len(times) - 1):
        current_segment.append((times[i], data[i]))
        if times[i + 1] - times[i] > inactivity_threshold:
            segments.append(current_segment)
            current_segment = []
    
    # Add the last segment
    if current_segment:
        segments.append(current_segment)
    
    return segments

# Splitting data
segments = split_data(times, data, DATA_RECORDING_INTERVAL * 20)

# Plotting
for i, segment in enumerate(segments):
    if segment:  # Check if segment is not empty
        x, y = zip(*segment)  # Unzip time and data
        plt.figure(i)
        plt.plot(x, y)
        plt.title(f'Segment {i+1}')
        plt.xlabel('Time')
        plt.ylabel('Data')

plt.show()
def send_serial_command(command):
    ser.write(command.encode())

# Example usage:
send_serial_command('your_command_here')
