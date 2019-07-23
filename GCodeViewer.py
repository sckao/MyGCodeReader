import numpy as np
import matplotlib.pyplot as plt

import math

class GetQuiverObject:

    mx = 0.
    my = 0.
    objX = 0.
    objY = 0.
    dr = 999999999.
    idx = -1

    key_val = ''

    def __init__(self, axes, objlist, colorV ):
        self.ax = axes
        self.objV = objlist
        self.colV = colorV
        self.press = None
        self.viewbounds = self.ax.viewLim.bounds
        #self.ax.set_autoscale_on( False )

    def objMatch(self, mx, my):
        i = 0
        self.idx = -1
        self.dr = 999999999.
        print(' matching objs')
        for ob in self.objV :
            x = ob[0]
            y = ob[1]
            dx = mx - x
            dy = my - y
            dr_ = math.sqrt( (dx*dx) + (dy*dy) )
            if dr_ < self.dr :
                self.dr = dr_
                self.idx = i
                self.objX = x
                self.objY = y
            i = i + 1

        if ( self.dr < 5 ) :
            print('>{:3d}'.format(self.idx) + ' points:{:.3f}'.format(self.objX) + ', {:.3f}'.format(self.objY) + ' dr = {:.3f}'.format(self.dr)
                  + ' mouse x: {:.3f}'.format(mx) + ' y: {:.3f}'.format(my) )
            self.press = self.idx, self.objX, self.objY, mx, my
            #print('>{:3d}'.format(self.press[0]) + ' points:{:.3f}'.format(self.press[1]) + ', {:.3f}'.format(self.press[2])
            #      + ' -> {:.3f}'.format(self.press[3]) + ', {:.3f}'.format( self.press[4]) )
            return True
        else:
            return False

    def key_press(self, event):

        self.key_val = event.key

    def key_release(self, event):

        self.key_val = ''

    def on_press(self, event):
        #if event.inaxes != self.ax.axes: return

        mx = event.xdata
        my = event.ydata
        #if self.key_val == 'control' :
        self.objMatch(mx, my)
        self.viewbounds = self.ax.viewLim.bounds
        print( ' - View Limit Bound : ', self.viewbounds  )



    def on_motion(self,event):
        if self.press is None : return
        if self.key_val == 'control' :
            mx = event.xdata
            my = event.ydata
            #if event.inaxes != self.ax.axes: return
            print('>{:3d}'.format(self.idx) + ') old points:{:.3f}'.format(self.objX) + ', {:.3f}'.format(self.objY)
                    + ' in list {:.3f}'.format( self.objV[self.idx][0] ) + '. {:.3f}'.format( self.objV[self.idx][1] ) )

            # Update position to current mouse position
            self.objV[self.idx][0] = mx
            self.objV[self.idx][1] = my
            print('>{:3d}'.format(self.idx) + ') new points:{:.3f}'.format(self.objV[self.idx][0] ) + ', {:.3f}'.format(self.objV[self.idx][1])  )

            # clear current plot and reset the xy limit
            self.ax.cla()
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            plt.xlim([self.viewbounds[0], self.viewbounds[0] + self.viewbounds[2]])
            plt.ylim([self.viewbounds[1], self.viewbounds[1] + self.viewbounds[3]])
            plt.grid(b=True, which='major')
            SetQuiver( self.ax, self.objV, self.colV, self.objV[0][0], self.objV[0][1] )
            self.ax.figure.canvas.draw()
        elif self.key_val == '' :
            self.viewbounds = self.ax.viewLim.bounds
            print( ' = View Limit Bound : ', self.viewbounds  )
            plt.xlim([self.viewbounds[0], self.viewbounds[0] + self.viewbounds[2]])
            plt.ylim([self.viewbounds[1], self.viewbounds[1] + self.viewbounds[3]])
        else :
            return


    def on_release(self, event):
        if self.key_val != 'control' : return

        self.press = None
        self.ax.cla()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        plt.xlim([self.viewbounds[0], self.viewbounds[0] + self.viewbounds[2]])
        plt.ylim([self.viewbounds[1], self.viewbounds[1] + self.viewbounds[3]])
        #plt.xlim([-10, 290])
        #plt.ylim([-10, 290])
        plt.grid(b=True, which='major')
        SetQuiver( self.ax, self.objV, self.colV, self.objV[0][0], self.objV[0][1] )
        self.ax.figure.canvas.draw()

    def objPick(self):

        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press )
        self.ax.figure.canvas.mpl_connect('key_press_event', self.key_press )
        self.ax.figure.canvas.mpl_connect('key_release_event', self.key_release )
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release )
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion )



def vMag( vec ):
    len =  math.sqrt( (vec[0]*vec[0]) + (vec[1]*vec[1]) )
    return len

def SetQuiver( ax, gV, colorV, X0 = 0. , Y0 = 0. ) :

    # adding vectors
    #X = gV[0][0]
    #Y = gV[0][1]
    X = X0
    Y = Y0
    j = 0
    for i in gV :
        dX = i[0] - X
        dY = i[1] - Y
        #print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
        ax.quiver( X, Y, dX, dY, angles='xy', scale_units='xy',scale=1, color= colorV[j], picker=5 )

        X += dX
        Y += dY
        j += 1



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

    # Setup call-back function
    qObj = GetQuiverObject( ax, gV, colorV )
    qObj.objPick()

    bounds = ax.viewLim.bounds
    print( ' View Limit Bound : ', bounds  )

    # adding retract points
    plt.scatter( sX, sY,s=20, c=sC, marker= '^')
    plt.scatter( rX, rY,s=20, c=rC, marker= 'o')

    SetQuiver( ax, gV, colorV )

    plt.show()

