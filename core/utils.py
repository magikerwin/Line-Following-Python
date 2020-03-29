import sys
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

def Error(text):
    print(text)
    sys.exit()

def plotPoint(point, color='red'):
    ca = plt.gca()
    ca.add_patch(Rectangle((point[0]-0.5, point[1]-0.5), 
                           1, 1, color=color))
    
def plotLine(point_a, point_b, color='red'):
    x1, y1 = point_a
    x2, y2 = point_b
    plt.plot([x1,x2], [y1,y2], color=color)

def plotWindow(window, color='red'):
    xmin, ymin, xmax, ymax = window
    # horizontal line
    for x in range(xmin, xmax+1+1):
        plotLine([x-0.5, ymin-0.5], [x-0.5, ymax+0.5], color)
    # vertical line
    for y in range(ymin, ymax+1+1):
        plotLine([xmin-0.5, y-0.5], [xmax+0.5, y-0.5], color)
