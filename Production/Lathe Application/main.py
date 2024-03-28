from commands import *
from structure import *
from application import *

queue = Queue()
queue.add(Command("cal"))
queue.add(Command("cal"))
queue.add(Command("move", (5, 0)))

queue.add(RandomWalk(10000,(1,10)))
run(queue)