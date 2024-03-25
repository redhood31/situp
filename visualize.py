import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import linecache
import numpy as np
from analyze import find_depth, dofilter, find_pitfalls
index = 0

angles = []
def animate(ind):
    plt.cla()
    global index
    with open("situp.txt", "r") as file:
        file.seek(0)

        # Read all lines into a list
        lines = file.readlines()
        for ind in range(index, len(lines), 1):
            angles.append(float(lines[ind]))
            index += 1
    filtered = dofilter(np.array(angles), 15)
    pitfalls = find_pitfalls(filtered)
    for point in pitfalls:
        depth = find_depth(filtered, point)
        print("DEPTH IS " , depth)
        if(depth != False):
            plt.axvline(x=point, color='green', linestyle='--', label=f'Vertical Line at x={point}', ymin = 0, ymax = depth)
            plt.vlines(x=point, ymin=0, ymax=depth, color='red', linestyle='solid', label=f'Vertical Line at x={point} with height')
    plt.plot(range(len(filtered)),  angles, color='blue')
    plt.plot(range(len(filtered)),  filtered, color='orange')
    
# print("THE LINE" , linecache.getline("situp.txt", 2))
ani = FuncAnimation(plt.gcf(), animate, interval=100)
plt.ylim(bottom=0) 
plt.tight_layout()
plt.show()


