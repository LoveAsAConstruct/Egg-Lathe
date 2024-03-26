def generate_sine_wave_command(amplitude, frequency, steps):
    commands = []
    for i in range(steps):
        commands.append(f"moveLinear {amplitude} {frequency}")
    return commands

def generate_zig_zag_command(amplitude, steps):
    commands = []
    direction = 1
    for i in range(steps):
        commands.append(f"moveLinear {amplitude * direction}")
        direction *= -1
    return commands

def generate_gradient_band_command(start_thickness, end_thickness, steps):
    commands = []
    thickness_step = (end_thickness - start_thickness) / steps
    for i in range(steps):
        thickness = start_thickness + i * thickness_step
        commands.append(f"moveLinear {thickness}")
    return commands

def generate_grid_command(longitude_lines, latitude_lines):
    commands = []
    for _ in range(longitude_lines):
        commands.append("rotateEgg 200")
    for _ in range(latitude_lines):
        commands.append("moveLinear 20")
    return commands
