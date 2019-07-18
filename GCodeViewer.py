import numpy as np
import matplotlib.pyplot as plt

import math

class GetQuiverObject:

    xpos = 0.
    ypos = 0.
    dr = 999999999.
    idx = -1

    def __init__(self, figure, objlist ):
        self.fig = figure
        self.objV = objlist

    def onclick(self, event):
        mx = event.xdata
        my = event.ydata

        i = 0
        self.idx = -1
        self.dr = 999999999.
        for ob in self.objV :
            x = ob[0]
            y = ob[1]
            dx = mx - x
            dy = my - y
            dr_ = math.sqrt( (dx*dx) + (dy*dy) )
            if dr_ < self.dr :
                self.dr = dr_
                self.idx = i
                self.xpos = x
                self.ypos = y
            i = i + 1

        if ( self.dr < 5 ) :
            print('>{:3d}'.format(self.idx) + ' points:{:.3f}'.format(self.xpos) + ', {:.3f}'.format(self.ypos) + ' dr = {:.3f}'.format(self.dr) )


    def objPick(self):

        self.fig.canvas.mpl_connect('button_press_event', self.onclick )



def vMag( vec ):
    len =  math.sqrt( (vec[0]*vec[0]) + (vec[1]*vec[1]) )
    return len

# gV is the positions of every X-Y movement
# hV is the positions of every Z movement
def ShowPath( gV, colorV, hV, hCol ):

    # setup cavas
    fig = plt.figure()
    fig.suptitle( 'G Code Path', fontsize=10, fontweight='bold')

    # one sub plot (x,y,index)
    ax = fig.add_subplot(111)
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    plt.xlim([-10, 290])
    plt.ylim([-10, 290])
    plt.grid(b=True, which='major')

    # X Y and color code for every Z movement
    sX = []
    sY = []
    sC = []
    rX = []
    rY = []
    rC = []
    for i in range( len(hV) ):
        if  hCol[i] == 'red' :
            sX.append( hV[i][0] )
            sY.append( hV[i][1] )
            sC.append( 'red' )
        else :
            rX.append( hV[i][0] )
            rY.append( hV[i][1] )
            rC.append( 'black' )


    # adding vectors
    X = 0
    Y = 0
    j = 0
    for i in gV :
        dX = i[0] - X
        dY = i[1] - Y
        #print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
        plt.quiver( X, Y, dX, dY, angles='xy', scale_units='xy',scale=1, color= colorV[j], picker=5 )

        X += dX
        Y += dY
        j += 1

    # adding retract points
    plt.scatter( sX, sY,s=20, c=sC, marker= '^')
    plt.scatter( rX, rY,s=20, c=rC, marker= 'o')

    #fig.canvas.mpl_connect('pick_event', onclick )
    qObj = GetQuiverObject( fig, gV )
    qObj.objPick()

    plt.show()

