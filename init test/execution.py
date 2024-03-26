# execution.py
# Example content - replace with actual pattern function calls as needed
from draw_functions import *
from pyserial import * 
def draw_pattern():
    print("Drawing a pattern...")
    for i in range (0,10):
        draw_zig_zag_band(i,10,200)
if __name__ == "__main__":
    draw_pattern()
