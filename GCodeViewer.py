import numpy as np
import matplotlib.pyplot as plt

import math

class GetQuiverObject:

    # mouse x,y position
    mx = 0.
    # object x,y,z,E position
    my = 0.
    objX = 0.
    objY = 0.
    objZ = 0.
    objE = 0.
    dr = 999999999.
    # index of object in the list
    idx = -1
    # gcode file I/O
    IO = None

    key_val = ''

    def __init__(self, axes, objlist, gfile ):
        self.ax = axes
        self.objV = objlist
        self.press = None
        self.viewbounds = self.ax.viewLim.bounds
        self.IO = gfile
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
                self.objZ = ob[2]
                self.objE = ob[3]
            i = i + 1

        if ( self.dr < 5 ) :
            print('>{:3d}'.format(self.idx) + '  Object x :{:.3f}'.format(self.objX) + ', y: {:.3f}'.format(self.objY) + ' dr = {:.3f}'.format(self.dr)
                  + ' mouse x: {:.3f}'.format(mx) + ' y: {:.3f}'.format(my) )
            self.press = self.idx, self.objX, self.objY, mx, my
            return True
        else:
            return False

    def key_press(self, event):

        self.key_val = event.key

    def key_release(self, event):

        self.key_val = ''
        self.press = None

    def on_press(self, event):

        if self.key_val == 'control' and event.button == 1 :
            print(' Modify Mode ')
            mx = event.xdata
            my = event.ydata
            #if self.key_val == 'control' :
            self.objMatch(mx, my)
            self.viewbounds = self.ax.viewLim.bounds
            #print( ' - View Limit Bound : ', self.viewbounds  )

        elif self.key_val == '' and event.button == 3 :
            print(' Read Only Mode ')
            mx = event.xdata
            my = event.ydata
            #if self.key_val == 'control' :
            self.objMatch(mx, my)
            self.viewbounds = self.ax.viewLim.bounds
            #print( ' - View Limit Bound : ', self.viewbounds  )

        else :
            pass


    def on_motion(self,event):
        if self.press is None : return
        if self.key_val == 'control' :
            mx = event.xdata
            my = event.ydata
            #if event.inaxes != self.ax.axes: return
            print('>{:3d}'.format(self.idx) + ') old points:{:.3f}'.format(self.objX) + ', {:.3f}'.format(self.objY)
                    + ' in list {:.3f}'.format( self.objV[self.idx][0] ) + '. {:.3f}'.format( self.objV[self.idx][1] ) )

            # Update position to current mouse position
            #self.IO.write( '; %d, %.3f, %.3f, %.3f, %.4f,  %.3f, %.3f \n'
            #               %(self.idx, self.objV[self.idx][0], self.objV[self.idx][1],  self.objV[self.idx][2], self.objV[self.idx][3],mx, my))
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
            SetQuiver( self.ax, self.objV, self.objV[0][0], self.objV[0][1] )
            self.ax.figure.canvas.draw()
        elif self.key_val == '' :
            mx = event.xdata
            my = event.ydata
            #x0 = self.objX
            #y0 = self.objY
            self.objV[self.idx][0] = mx
            self.objV[self.idx][1] = my
            print(' Pos ( %.3f, %.3f, %.3f,  %.4f ) ' %(self.objX, self.objY, self.objZ, self.objE, ))

            # clear current plot and reset the xy limit
            self.ax.cla()
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            #self.viewbounds = self.ax.viewLim.bounds
            #print( ' = View Limit Bound : ', self.viewbounds  )
            plt.xlim([self.viewbounds[0], self.viewbounds[0] + self.viewbounds[2]])
            plt.ylim([self.viewbounds[1], self.viewbounds[1] + self.viewbounds[3]])
            plt.grid(b=True, which='major')
            SetQuiver( self.ax, self.objV, self.objV[0][0], self.objV[0][1] )
            self.ax.figure.canvas.draw()
            # set the point back to its original position
            self.objV[self.idx][0] = self.objX
            self.objV[self.idx][1] = self.objY

        else :
            return


    def on_release(self, event):
        #if self.key_val != 'control' : return

        if self.key_val == '' and event.button == 1 : return

        self.press = None
        self.ax.cla()
        # Re-Draw plots
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        plt.xlim([self.viewbounds[0], self.viewbounds[0] + self.viewbounds[2]])
        plt.ylim([self.viewbounds[1], self.viewbounds[1] + self.viewbounds[3]])
        #plt.xlim([-10, 290])
        #plt.ylim([-10, 290])
        plt.grid(b=True, which='major')
        SetQuiver( self.ax, self.objV, self.objV[0][0], self.objV[0][1] )
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

def SetQuiver( ax, gV,  X0 = 0. , Y0 = 0. ) :

    # gV[0 ~ 5] : x, y, z, E, color, moveType
    # move type <= 3 : only X,Y movement
    # move type == 4 : only Z movement

    # adding vectors
    X = X0
    Y = Y0
    sX = []
    sY = []
    sC = []
    rX = []
    rY = []
    rC = []
    j = 0
    for i in gV :

        # XY movement and not the last point
        if  i[5] != 4 and j != len(gV)-1  :

            dX = i[0] - X
            dY = i[1] - Y
            #print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
            ax.quiver( X, Y, dX, dY, angles='xy', scale_units='xy',scale=1, color= i[4], picker=5 )

            X += dX
            Y += dY
        # Z only movement - get information for a scatter plot
        if i[5] == 4 :
            if i[2] == 'green' :
                sX.append( i[0] )
                sY.append( i[1] )
                sC.append( 'green' )
            else :
                rX.append( i[0] )
                rY.append( i[1] )
                rC.append( 'purple' )

        j = j+1

    # adding retract points
    ax.scatter( sX, sY,s=60, marker= '^', facecolors='none', edgecolors=sC )
    ax.scatter( rX, rY,s=50, marker= 'o', facecolors='none', edgecolors=rC )



# gV contains the positions of every X-Y movement, color code and moveType
# Draw the path in this particular layer
def ShowPath( gV, gfile, xlimL = -5, xlimR = 355, ylimB = -5, ylimT = 305 ):

    # setup cavas
    fig = plt.figure( figsize=(8,8) )
    fig.suptitle( 'G Code Path', fontsize=10, fontweight='bold')

    # one sub plot (x,y,index)
    ax = fig.add_subplot(111)
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # Plot XY limit and grid
    plt.xlim([ xlimL, xlimR])
    plt.ylim([ ylimB, ylimT])
    plt.grid(b=True, which='major')

    # Setup call-back function
    qObj = GetQuiverObject( ax, gV, gfile )
    qObj.objPick()

    #bounds = ax.viewLim.bounds
    #print( ' View Limit Bound : ', bounds  )

    SetQuiver( ax, gV, gV[0][0], gV[0][1]  )

    plt.show()

