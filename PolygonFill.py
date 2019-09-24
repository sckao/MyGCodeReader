import math
import numpy as np
import matplotlib.pyplot as plt
from Polygram import Polygrams

def sortX( vec ):
    return vec[0]

def sortY( vec ):
    return vec[1]

class PolygonFill:


    def __init__(self, nside , radius, angle ):

        # n must be >=  3
        self.n = nside
        self.r = radius
        self.angle = angle
        self.pos = []
        self.beadwidth = 0.75


    def create(self):

        # starting angle for the polygon
        polyObj = Polygrams()
        polyObj.Create( self.n , self.r, self.angle  )

        for i in range( self.n) :

            self.pos.append( [ polyObj.x[i], polyObj.y[i]] )



    def shiftCopy(self, pos , dx, dy):

        cp = []
        for i in range( len( pos) ) :

            x = pos[i][0] + dx
            y = pos[i][1] + dy
            cp.append( [x,y] )

        return cp


    def imageCopy(self, pos, XorY = 'x'  ):

        minY = pos[0][1]
        maxX = pos[0][0]
        for i in range( len(pos) ):

            if pos[i][1] < minY :
                minY = pos[i][1]

            if pos[i][0] > maxX :
                maxX = pos[i][0]


        cp = []
        for i in range( len(pos) ):

            dy = pos[i][1] - minY
            dx = maxX - pos[i][0]
            if  XorY == 'y' or XorY == 'Y' :
                x = pos[i][0]
                y = pos[i][1] - (dy*2)
                cp.append( [ x,y ] )
            if  XorY == 'x' or XorY == 'X' :
                x = pos[i][0] + (2*dx)
                y = pos[i][1]
                cp.append( [ x,y ] )

        return cp

    def getResult(self, pos= [], xlist=[], ylist=[] ):


        for i in range( len(pos)) :

            xlist.append( pos[i][0] )
            ylist.append( pos[i][1] )

    # Create upper or lower part of the polygon chains
    # ds < 0 is for the lower part
    def createArc(self, xc, yc, ds, n, pos):

        theta = math.pi / (n+1)
        r = abs(ds/2.)

        # Only add the initial point if this is the starting point
        if len(pos) < 1 :
            pos.append( [x0,y0] )
        j = n
        max_dy = 0
        # This part only fill intermediate points
        k = 1
        for i in range(n) :

            # upper part of arc
            if ds > 0 :
                j = n - i
            # bottom part of arc
            if ds < 0 :
                j = -1*(i+1)
            dx = r*math.cos( theta*j )
            dy = r*math.sin( theta*j )

            if abs(dy) > max_dy :
                max_dy = abs(dy)

            x = xc + dx
            y = yc + dy
            print('   (j=%d) , theta = %.3f, x=%.3f y= %.3f' %(j, theta*j, x, y))
            pos.append( [x,y] )

        return max_dy


    # k is number of layer for the polygon
    def createChain(self,x0,y0, Lx, ds, dL, n, m, k = 1 ):

        i = 1
        arcs = []
        #angle = (math.pi/4)*(n/(n+1))
        d = self.beadwidth
        angle1 = math.pi/((n+1)*2)
        angle2 = math.pi/((m+1)*2)
        cor =  (d/math.cos(angle1)) - (d*math.tan(angle1))

        x = x0
        y = y0 + ((k-1)*d)
        h1 = 0
        arcs.append([x,y])
        print( ' *  Start from xy = (%.3f , %.3f)' %( x, y))
        x = x0 + dL - ((k-1)*cor)
        y = y0 + ((k-1)*d)
        # adding the first segment
        arcs.append([x,y])
        print( ' ** Start from xy = (%.3f , %.3f)' %( x, y))
        xc = x0 + dL + (ds/2)
        yc = y0
        while  Lx >= (ds+dL)*i :

            r = ds + ((k-1)*d*2/math.cos(angle1))

            print(" (%d) xc,yc,r =  %.3f, %.3f , %.3f" %(i, xc,yc, r))
            h1 = self.createArc( xc, yc, r, n, arcs )
            if (ds+dL)*(i+1) <= Lx :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                print( ' -- segment[%d] start xy = (%.3f , %.3f)' %(i, x, y))
                x = arcs[-1][0] + dL - ((k-1)*cor*2)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                print( ' -- segment[%d] end xy = (%.3f , %.3f)' %(i, x, y))
                print('  -- continue ')
            else :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                print( ' == segment[%d] end xy = (%.3f , %.3f)' %(i, x, y))
                x = arcs[-1][0] + dL - ((k-1)*cor) + ((k-1)*d)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                print('  -- end  ')

            print( ' [%d] xy = (%.3f , %.3f)' %(i, x, y))
            xc = xc + dL + ds
            i = i+1

        # shift downward
        y = y - (d*(2*k-1))
        arcs.append( [x, y])
        x = arcs[-1][0] - dL +  ((k-1)*cor) - ((k-1)*d)
        arcs.append( [x, y])
        yc = yc - d
        xc = xc - dL - ds
        i = i-1
        h2 = 0
        j = 1
        cor =  (d/math.cos(angle2)) - (d*math.tan(angle2))
        print(" >> xc,yc = %.3f, %.3f " %(xc,yc))
        while i > 0 :


            r = -1*ds - ((k-1)*d*2/math.cos(angle2))
            print(" (%d) xc,yc,r =  %.3f, %.3f , %.3f" %(i, xc,yc, r))
            h2 = self.createArc( xc,yc, r, m, arcs )
            if i > 1 :
                #x = arcs[-1*(m+1)][0] - ds
                #y = arcs[-1*(m+1)][1]
                x = x - ds - ((k-1)*cor*2)
                y = y0 -d - ((k-1)*d)
                arcs.append( [x, y] )
                print( ' -- segment[%d] start xy = (%.3f , %.3f)' %(i, x, y))
                #x = arcs[-1][0] -dL
                #y = arcs[-1][1]
                x = x - dL + ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d)
                print( ' -- segment[%d] end xy = (%.3f , %.3f)' %(i, x, y))
                arcs.append( [x, y] )
            else :
                #x = arcs[-1*(m+1)][0] - ds
                #y = arcs[-1*(m+1)][1]
                x = x  - ds - ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d)
                arcs.append( [x, y] )

            print( ' -> [%d] xy = (%.3f , %.3f)' %(i, x, y))
            xc = xc - dL - ds
            i = i-1
            j = j+1

        x = x -dL + ((k-1)*cor)
        y = y
        arcs.append([x,y])
        print( ' ** End at  xy = (%.3f , %.3f)' %( x, y))
        h = h1+h2
        return arcs, h

    def unitSize(self, ds, dL, n, m):
        arcs, h = self.createChain( 0, 0,dL+ds, ds, dL, n, m)
        width = ds
        height = h + self.beadwidth
        return width, height


    def FillAreaN(self, xV, yV, LV, ds, dL, n, m, k = 1):

        iniX = xV[0]
        iniY = yV[0]
        x = []
        y = []
        for j in range(k) :

            j = j+1
            for i in range( len(LV) ) :
                print(' Printing Row %d' %(i))
                y_start = yV[i] + (j-1)*self.beadwidth
                # Move to next row
                if xV[i] > iniX :
                    arc = []
                    arc.append( [ iniX, y_start ])
                    self.getResult( arc, x,y)
                if xV[i] < iniX :
                    arc = []
                    iniY = y[-1]
                    arc.append( [ xV[i], iniY])
                    self.getResult( arc, x,y)

                # Move to starting point of this row
                iniX = xV[i]
                iniY = yV[i]
                if i%2 == 0 :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, n, m, j)
                    self.getResult( arcs, x,y)
                else :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, m, n, j)
                    self.getResult( arcs, x,y)

        return x, y

    # Not complete yet
    def partition(self, shell, ds, dL, n, m ):

        # Find the min x,y and max x,y
        max_x = -9999.
        max_y = -9999.
        min_x = 9999.
        min_y = 9999.
        for i in range( len(shell)) :

            x = shell[i][0]
            y = shell[i][0]
            if x > max_x :
                max_x = x
            if x < min_x :
                min_x = x
            if y > max_y :
                max_y = y
            if y < min_y :
                min_y = y

        wShell = max_x - min_x
        hShell = max_y - min_y

        # Find the unit width(w0) and height(h0)
        w0 , h0 = self.unitSize( ds, dL, n, m)

        #
        nw = int(wShell/w0)
        nh = int(hShell/h0)




##################################
#       Testing PolygonFill      #
##################################

x= []
y= []

polychain = PolygonFill(4,10,0)
iniX = 0
iniY = 5
n_up = 2
n_low = 2
ds = 15
dL = 5
nLayer = 3

w0 , h0 = polychain.unitSize(ds,dL,n_up, n_low)
print( 'Unit size = %.3f , %.3f' %(w0, h0))
LV = [50,30,60,78]
xV = [0,20,20,0]
yV = []
for i in range(4):
    yV.append(iniY)
    iniY = iniY - h0 - ((polychain.beadwidth)*(2*nLayer -1 ))

x, y = polychain.FillAreaN(xV, yV, LV, ds, dL, n_up, n_low, nLayer)

'''
arcs, h = polychain.createChain( iniX, iniY,70,ds, dL, n_up, n_low, 1)
polychain.getResult( arcs, x,y)
arcs, h = polychain.createChain( iniX, iniY,70,ds, dL, n_up, n_low, 2)
polychain.getResult( arcs, x,y)
arcs, h = polychain.createChain( iniX, iniY,70,ds, dL, n_up, n_low, 3)
polychain.getResult( arcs, x,y)
'''


# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Polygon Test', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([-5, 95])
plt.ylim([-55, 25])
plt.grid(b=True, which='major')
ax.scatter( x,  y,  s=50, marker= 'o', facecolors='red', edgecolors='red' )

# Start Routing (x,y) -> (xt,yt) -> (x,y)
print( ' total point %d ' %( len(x)) )
x_ = x[0]
y_ = y[0]
nPoint = len( x )
for i in range( nPoint -1 ) :
    dX = x[i+1] - x_
    dY = y[i+1] - y_
    # print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
    ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=2)

    x_ = x[i+1]
    y_ = y[i+1]


plt.show()