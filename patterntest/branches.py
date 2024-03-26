import turtle
import random
t = turtle.Turtle()
t.screen.screensize(200,200)
turtle.speed(0)
t.hideturtle()
while(True):
    t.forward(random.randint(0,50))
    t.right(random.randint(-1,1)*180)
    t.sety(random.randint(-5,5)+t.ycor())
    if(random.randint(0,10) == 1):
        t2 = turtle.Turtle()
        t2.hideturtle()
        t2.pu()
        t2.setpos(t.pos())
        t2.pd()
        t2.setheading(90)
        t2.forward(random.randint(0,50))
