
import serial
import time
import math
import turtle
import re
import pygame
import colorsys

STEPS = 200
interleave = False
COMMAND_TIME = 663723456
class Command:
    def __init__(self, type, value="None", layer = 0, split_pattern=r"[\{\[\|\]\}]"):
        self.type = type.lower()
        self.value = value
        self.commands = []
        self.layer = layer
        self.movement = None
        if self.type == "raw":
            for subcommand in re.split(split_pattern, value):
                if subcommand:  # This checks if the subcommand is not an empty string
                    self.commands.append(subcommand)
        elif self.type == "move":
            # Assuming 'value' is a sequence like a list or tuple with two elements
            if isinstance(value, (list, tuple)) and len(value) == 2:
                if interleave:
                    movement = (round(value[0]*2), round(value[1]*2))
                else:
                    movement = (round(value[0]), round(value[1]))
            else:
                movement = (0, 0)
            self.movement = movement
            self.commands.append(f"C-MX {movement[0]}")
            self.commands.append(f"C-MY {movement[1]}")
        elif self.type in ["cal", "calibrate"]:
            self.commands.append("C-CB")
            
    def execute(self, serial):
        for command in self.commands:
            self.send_command(command, serial)
        return True
    
    def send_command(self, command, ser):
        print(f"Sending: {command}")
        ser.write((command + "\n").encode())
        start_time = time.time()
        while True:
            if abs(start_time-time.time()) > 5:
                print("Breaktime")
                return
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                if response == "-CC":
                    print(f"{response} recieved")
                    return response
            
    
    
class Queue():
    def __init__(self):
        self.queue = []
        self.length = 0
        self.layers = set()
        self.position = (0,0)
        
    def add(self, commandset):
        if isinstance(commandset, list):
            if isinstance(commandset[0], Command):
                if commandset[0].layer == None:
                    for command in commandset:
                        command.layer = len(self.layers)
            for command in commandset:
                self.add(command)
        elif isinstance(commandset, Command):
            if commandset.layer == None:
                commandset.layer = len(self.layers)
            self.queue.append(commandset)
            self.length += 1
            self.layers.add(commandset.layer)
            if commandset.type == "move":
                self.position = (self.position[0]+commandset.value[0],self.position[1]+commandset.value[1])
            elif commandset.type == "calibrate":
                self.position = (0,0)
    def execute(self, serial, window = None):
        print(f"executing queue with length {len(self.queue)}")
        if window != None:
            windowExecution = True
            window.progress = 0
        else:
            windowExecution = False
        commandtime = COMMAND_TIME
        commands = 1
        for command in self.queue:
            start_time = time.time_ns()
            command.execute(serial)
            if windowExecution:
                window.progress += 1
                window.commandTime = commandtime
                window.consoleText = command.commands[0]
                window.updateAll()
            commandtime = commandtime + (time.time_ns() - start_time)
            commands += 1
            window.commandtime = commandtime/commands
            print(commandtime)
            
    def get_layer_colors(self):
        """
        Generate unique colors for each layer, ensuring high contrast with a gray background.
        Returns a dictionary mapping layer numbers to RGB color tuples.
        """
        num_layers = len(self.layers)
        layer_colors = {}
        for i, layer in enumerate(sorted(self.layers)):
            hue = i / num_layers  # Hue divided evenly among layers
            saturation = 0.75  # High saturation for vivid colors
            value = 0.75 if (i % 2 == 0) else 0.5  # Alternate value for even more distinction
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            layer_colors[layer] = tuple(int(255 * c) for c in rgb)
        return layer_colors
    
    def previewPygame(self, bounds=(False, True), interleave=False, surface=None, executionIndex = None):
        def _draw_commands(draw_surface, x, y, bounds, interleave, pen_down, scalar = 1):
            # Placeholder for drawing logic
            # Start position for drawing
            start_pos = (x, y)
            origin = (x, y)
            skip = False
            pygame.draw.rect(draw_surface,(200,200,200),rect=pygame.Rect(x,y,scalar*STEPS,scalar*STEPS),border_radius=5)
            index = 0
            for command in self.queue:
                if command.type == "move": 
                    # Set color based on layer if pen is down
                    if pen_down and not skip:
                        if executionIndex != None and index<executionIndex:
                            color = (0,0,0)
                            index += 1
                        else:
                            color = self.get_layer_colors()[command.layer]
                    else:
                        color = (0, 0, 0) # Or some default color, if needed

                    # Calculate new position
                    if interleave:
                        x += (command.movement[0]*scalar) / 2
                        y += (command.movement[1]*scalar) / 2
                    else:
                        x += command.movement[0] * scalar
                        y += command.movement[1] * scalar
                    # Handle bounds
                    if bounds[1]:
                        end_pos = (int(x), int(y))
                        # If y crosses the upper boundary
                        if (y - origin[1]) / scalar > STEPS:
                            pygame.draw.line(draw_surface, color, start_pos, (start_pos[0], STEPS * scalar + origin[1]))
                            # Calculate new y, wrapping to the bottom
                            y = ((y / scalar - origin[1]) % STEPS) * scalar + origin[1]
                            # Adjust start_pos to the new wrapped position to avoid vertical band
                            start_pos = (start_pos[0], origin[1])
                            pygame.draw.line(draw_surface, color, start_pos, (start_pos[0], y))
                            # Update start_pos to reflect the actual starting position after wrap
                            start_pos = (start_pos[0], y)

                        # If y crosses the lower boundary
                        elif (y - origin[1]) / scalar < 0:
                            pygame.draw.line(draw_surface, color, start_pos, (start_pos[0], origin[1]))
                            # Calculate new y, wrapping to the top
                            y = STEPS * scalar + origin[1] - ((origin[1] - y / scalar) % STEPS) * scalar
                            # Adjust start_pos to reflect the wrap to the top edge
                            start_pos = (start_pos[0], STEPS * scalar + origin[1])
                            pygame.draw.line(draw_surface, color, start_pos, (start_pos[0], y))
                            # Update start_pos for the next iteration
                            start_pos = (start_pos[0], y)
                        
                        
                    if bounds[0] and ((x - origin[0])/scalar > 200 or (x - origin[0])/scalar < 0):
                        x = ((x/scalar - origin[0]) % 200)*scalar + origin[0]
                        skip = False
                    # Draw line if pen is down
                    stepped_lines = True
                    end_pos = (int(x), int(y))
                    if True:
                        if stepped_lines:
                            if color == (0,0,0):
                                width = 3
                            else:
                                width = 1
                            pygame.draw.line(draw_surface, color, start_pos, (end_pos[0], start_pos[1]), width)
                            pygame.draw.line(draw_surface, color, (end_pos[0], start_pos[1]), end_pos, width)
                        else:
                            pygame.draw.line(draw_surface, color, start_pos, end_pos)
                    start_pos = end_pos
                    if skip:
                        skip = False

                elif command.type == "calibrate":
                    x, y = origin
                    skip = True

                elif command.type == "pen_up":
                    pen_down = False

                elif command.type == "pen_down":
                    pen_down = True

                
                    
        margin = 0
        
        if surface is None:
            # Initialize Pygame for standalone window
            pygame.init()
            scalar = 2
            margin = 25
            bedsize = int(STEPS*scalar)+2*margin
            # Window dimensions for standalone mod
            width, height = int(STEPS*scalar)+2*margin, int(STEPS*scalar)+2*margin
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Preview")

            # This is the drawing surface for a standalone window
            draw_surface = screen
        elif surface == False:
            scalar = 2
            margin = 0
            bedsize = int(STEPS*scalar)
            # Window dimensions for standalone mod
            width, height = int(STEPS*scalar), int(STEPS*scalar)
            screen = pygame.Surface((width,height))
            draw_surface = screen
        else:
            # Use the provided surface for drawing
            draw_surface = surface
            width, height = surface.get_size()
            bedsize = min(width,height)

        # Initial position and pen state
        x, y = margin, margin
        pen_down = True  # Pen starts in the down position

        if surface is None:
            running = True
            clock = pygame.time.Clock()

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Clear screen or surface
                draw_surface.fill((255, 255, 255))

                _draw_commands(draw_surface, x, y, bounds, interleave, pen_down, scalar)

                pygame.display.flip()
                clock.tick(60)

            pygame.quit()
        else:
            # If drawing on an existing surface, just call the drawing logic directly
            # Clear the provided surface before drawing
            draw_surface.fill((255, 255, 255))
            _draw_commands(draw_surface, x, y, bounds, interleave, pen_down, bedsize/STEPS)
        if surface == False:
            return draw_surface

    def preview(self, bounds = (True,True)):
        td = turtle.Turtle("classic")
        #td.hideturtle()
        td.setpos(0,0)
        td.pd()
        td.speed(0)
        for command in self.queue:
            #print(f"command: {command}")
            if command.type == "move":
                td.color(self.get_layer_colors()[command.layer])
                print(command.movement)
                if interleave:
                    td.setx(td.xcor() + command.movement[0]/2)
                    td.sety(td.ycor() + command.movement[1]/2)
                else:
                    td.setx(td.xcor() + command.movement[0])
                    td.sety(td.ycor() + command.movement[1])
            elif command.type == "calibrate":
                td.setx(0)
                td.sety(0)
            if bounds[1] and (td.ycor() > STEPS or td.ycor() < 0):
                td.pu()
                td.sety(td.ycor()%STEPS)
                td.pd()
            if bounds[0] and (td.xcor() > 200 or td.xcor() < 0):
                td.pu()
                td.setx(td.xcor()%200)
                td.pd()
    