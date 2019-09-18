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


    def createArc(self, x0, y0, ds, n, pos):

        theta = math.pi / (n+1)
        r = abs(ds/2.)

        xc = x0 + (ds/2)
        yc = y0

        if len(pos) < 1 :
            pos.append( [x0,y0] )
        j = n
        for i in range(n) :
            if ds > 0 :
                j = n - i
            if ds < 0 :
                j = -1*(i+1)
            dx = r*math.cos( theta*j )
            dy = r*math.sin( theta*j )

            x = xc + dx
            y = yc + dy
            print(' j=%d , theta = %.3f, x=%.3f y= %.3f' %(j, theta*j, x, y))
            pos.append( [x,y] )

        pos.append( [x0 + ds ,y0] )
        x0 = x0+ds
        y0 = y0


    def fillMethod(self,x0,y0, Lx, ds, dL, n, m ):

        i = 0
        arcs = []
        x = x0
        y = y0
        while  Lx >= ds*(i+1) :

            self.createArc( x, y, ds, n, arcs )
            if ds*(i+1) < Lx :
                x = arcs[-1][0] + dL
                y = arcs[-1][1]
                arcs.append( [x, y] )
            else :
                x = arcs[-1][0]
                y = arcs[-1][1]
                arcs.append( [x, y] )

            print( ' [%d] xy = (%.3f , %.3f)' %(i, x, y))

            i = i+1

        y = y-0.5
        arcs.append( [x, y])

        while i > 0 :

            self.createArc( x,y, -1*ds, m, arcs )
            if i > 1 :
                x = arcs[-1][0] -dL
                y = arcs[-1][1]
                arcs.append( [x, y] )
            else :
                x = arcs[-1][0]
                y = arcs[-1][1]
                arcs.append( [x, y] )

            print( ' -> [%d] xy = (%.3f , %.3f)' %(i, x, y))
            i = i-1


        return arcs


x= []
y= []

polychain = PolygonFill(4,10,0)
arcs = polychain.fillMethod(0,5,40,10, 5, 2, 2)
polychain.getResult( arcs, x,y)

'''
poly = PolygonFill(3,10., math.pi/2)
poly.create()
poly.getResult( poly.pos, x,y )
xcp = poly.imageCopy( poly.pos, 'x' )
poly.getResult( xcp, x,y )
ycp1 = poly.imageCopy( xcp, 'y' )
poly.getResult( ycp1, x, y)
ycp2 = poly.imageCopy( poly.pos, 'y' )
poly.getResult( ycp2, x, y)
'''

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Polygon Test', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([-5, 55])
plt.ylim([-15, 15])
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
    ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=5)

    x_ = x[i+1]
    y_ = y[i+1]



plt.show()