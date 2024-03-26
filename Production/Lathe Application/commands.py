from structure import *
import math
import random
xmax = STEPS

def SineBand(amplitude, frequency, layer = 0,steps = STEPS):
    queue = []
    for i in range(0, steps):
        queue.append(Command("move", (math.cos(i/200*frequency*2*math.pi)*amplitude/4,1), layer))
    return queue

def Circle(radius, layer=0, resolution=None, center=True):
    if resolution is None:
        # Adjust resolution dynamically with a minimum value to ensure smoothness
        resolution = max(12, round(radius * 2 * math.pi))

    mult = radius / (2 * (resolution / (4 * math.pi)))
    
    def circleCoordinates(angle):
        # Calculate movement based on the derivative of the circle's parametric equations
        return (-math.sin(angle) * mult, math.cos(angle) * mult)
    
    queue = []
    circle_completion = 0
    movement_overflow = (0, 0)
    totalMovement = (0, 0)

    if center:
        # Move to the circle's edge if centered
        initial_move = (radius/2, 0)
        queue.append(Command("move", initial_move, layer))
        totalMovement = initial_move

    while circle_completion < 2 * math.pi:
        circle_completion += 2 * math.pi / resolution
        if circle_completion > 2 * math.pi:
            # Ensure we don't overshoot the last segment
            circle_completion = 2 * math.pi
        circle_coords = circleCoordinates(circle_completion)

        # Include overflow from the previous step
        movement = (movement_overflow[0] + circle_coords[0], movement_overflow[1] + circle_coords[1])
        rounded_movement = (round(movement[0]), round(movement[1]))
        movement_overflow = (movement[0] - rounded_movement[0], movement[1] - rounded_movement[1])

        if rounded_movement != (0, 0):
            queue.append(Command("move", rounded_movement, layer))
            totalMovement = (totalMovement[0] + rounded_movement[0], totalMovement[1] + rounded_movement[1])

    if center:
        # Correct any minor discrepancies to ensure the circle completes accurately
        correction_move = (initial_move[0] - totalMovement[0], initial_move[1] - totalMovement[1])
        if correction_move != (0, 0):
            queue.append(Command("move", correction_move, layer))

    return queue

def ZigZagBand(amplitude, frequency, layer = 0, steps = STEPS):
    queue = []
    direction = 1
    movement = 0
    for i in range(steps):
        if i%frequency == 0:
            direction *= -1
        movement += amplitude*direction/(frequency)
        if abs(round(movement)) > 0:
            print(f"moving {movement}")
            queue.append(Command("move", (movement/2,1),layer))
            movement = 0
        else:
            queue.append(Command("move", (0,1),layer))
    return queue

def Band(thickness = 1, steps = STEPS): 
    queue = []
    for i in range (0,thickness):
        queue.append(Command("move", (0, steps)))
        queue.append(Command("move", (1,0)))
    queue.append(Command("move", (-thickness,0)))
    return queue

def LonLatLines(londiv=10, latdiv=10, layer = None, steps = (STEPS, STEPS)):
    queue = []
    queue.append(Command("calibrate",layer = layer))
    for i in range(0, londiv):
        queue.append(Command("move", (0,math.floor(steps[1]/londiv)),layer))
        queue.append(Command("move", (steps[0], 0),layer))
        queue.append(Command("move", (-steps[0], 0),layer))
    queue.append(Command("calibrate",layer = layer))
    for i in range(0, latdiv):
        queue.append(Command("move", (math.floor(steps[0]/latdiv),0),layer))
        queue.append(Command("move", (0, steps[1]),layer))
    return queue

def RandomWalk(iterations = 100, distancebounds = (1,10), pos = (0,0), layer = None, clipping = (True,False), vertchance = 1, circlechance = 0):
    queue = []
    currentPos = (pos[0],pos[1])
    for i in range(0, iterations):
        if circlechance != 0 and random.randint(0,1/circlechance) == 0:
            for command in Circle(random.randint(0,10), layer):
                queue.append(command)
        if random.randint(0,1) == 1:
            m = 1
        else:
            m = -1
        d = m*random.randint(distancebounds[0],distancebounds[1])
        if vertchance != 0 and random.randint(0,round(1/vertchance)) == 1:
            coord = (0, d)
            
        else:
            coord = (d,0)
        currentPos = (currentPos[0] + coord[0], currentPos[1] + coord[1])
        if (currentPos[0] > xmax or currentPos[0] < 0) and clipping[0]:
            iterations += 1
            currentPos = (currentPos[0] - coord[0], currentPos[1] - coord[1])
        elif (currentPos[1] > STEPS or currentPos[1] < 0) and clipping[1]:
            iterations += 1
            currentPos = (currentPos[0] - coord[0], currentPos[1] - coord[1])

        else:
            queue.append(Command("move", coord,layer))
        
            
    return queue