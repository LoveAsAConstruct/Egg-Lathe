from commands import *
from structure import *
from application import *

queue = Queue()
queue.add(Command("cal"))
queue.add(Command("cal"))

queue.add(Command("move", (50,0)))
queue.add(RandomWalk(5000,(5,5),vertchance=0.3))

#queue.add(RandomWalk(10000,(1,10)))

MainWindow(queue)