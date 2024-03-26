import serial
import time
import math

# Initialize serial connection (Replace '/dev/cu.usbmodem101' with your actual port)
ser = serial.Serial('/dev/cu.usbmodem101', 9600, timeout=1)
time.sleep(2)  # Allow time for the connection to establish

def send_command(command):
    print(f"Sending: {command}")
    ser.write((command + "\n").encode())
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print("Arduino:", response)
            break

def draw_sine_wave_band(amplitude, frequency, steps):
    for i in range(steps):
        linear_movement = int(amplitude * math.sin(2 * math.pi * frequency * (i / steps)))
        send_command(f"moveLinear {linear_movement}")
        send_command("rotateEgg 1")

def draw_zig_zag_band(amplitude, frequency, steps):
    direction = 1
    for i in range(steps):
        if i % frequency == 0:
            direction *= -1
        send_command(f"moveLinear {amplitude * direction}")
        send_command("rotateEgg 1")

def draw_gradient_band(start_thickness, end_thickness, bands):
    thickness_step = (end_thickness - start_thickness) / bands
    for i in range(bands):
        thickness = start_thickness + i * thickness_step
        send_command(f"moveLinear {thickness}")
        send_command("rotateEgg 200")  # Adjust the 200 steps based on your setup for a full rotation
        send_command(f"moveLinear -{thickness}")  # Return to start position

def draw_grid(longitude_lines, latitude_lines):
    for _ in range(longitude_lines):
        send_command("rotateEgg 200")  # Full rotation
        send_command(f"moveLinear {200 // latitude_lines}")  # Adjust movement for latitudinal spacing
    for _ in range(latitude_lines):
        send_command(f"moveLinear {200 // latitude_lines}")  # Move linearly for the next longitudinal line
        send_command("rotateEgg 200")  # Full rotation for longitudinal line
        
        
if __name__ == "__main__":
    # Example: Draw a sine wave band around the egg
    """
    send_command("moveLinear 100")
    for i in range (0,10):
        draw_zig_zag_band(i,10,200)
    """
    send_command("calibrate")
    send_command("moveLinear 50")
    #draw_grid(10,10)
    for i in range(0,20):
        draw_sine_wave_band((20-i)*1.5,(20-i),200)
    ser.close()  # Close the serial connection