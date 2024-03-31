from commands import *
from structure import *
from application import *

queue = Queue()
queue.add(Command("calibrate"))
queue.add(Command("move", (200, 0)))
for i in range(0,8):
    queue.add(ZigZagBand(10*i,10))
queue.add(Command("calibrate"))
queue.add(Command("move", (100, 0)))
for i in range(0,5):
    queue.add(Command("calibrate"))
    queue.add(Command("move", (100, 0)))
    queue.add(SineBand(7,2**i))
    
queue.add(Command("calibrate"))
for i in range(0,7):
    queue.add(Command("move", (i*2, 0)))
    queue.add(Band())
run(queue)