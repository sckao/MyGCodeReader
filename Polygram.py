import math
import numpy as np
import matplotlib.pyplot as plt

class Polygrams:

    # number of legs/sides
    n = 5
    # inner radius of the ploygon
    r = 10
    # inner angle
    delta = -1.*math.pi / 2
    theta = 2.*math.pi / n

    # points on the circle
    x = []
    y = []
    # slope and intercept for the side lines : y = mx+ d
    m = []
    d = []
    # position of resolved tip
    xt = []
    yt = []
    # Routing path
    u=[]
    v=[]

    # Flow Rate
    Eval = 1.
    Fval = 4000.

    def __init__(self, n_ = 5 ,  r_ = 10 ):
        self.n = int(n_)
        self.r = float(r_)
        self.delta = -1.*math.pi / 2
        self.theta = 2.*math.pi / self.n
        self.rho = self.Eval*60 / self.Fval

    def SetParameters(self, n_, r_, delta_  = -1.*math.pi /2 ):
        self.n = int(n_)
        self.r = float(r_)
        self.delta = delta_
        self.theta = 2.*math.pi / self.n
        self.x = []
        self.y = []
        self.m = []
        self.d = []
        self.xt = []
        self.yt = []
        self.u = []
        self.v = []

    # points on the circle
    def GetPolygon(self):
        # Compute n points of polygon
        for i in range( self.n ):
            self.x.append( self.r*math.cos(self.theta*i + self.delta) )
            self.y.append( self.r*math.sin(self.theta*i + self.delta) )
            #print( ' (%d) Angle = %.3f , x =%.3f y =%.3f ' %( i, math.degrees(self.theta*i), self.x[i], self.y[i] ) )


    # Solve n side of the polygon : y = mx + d
    def GetLine(self):

        for i in range( self.n ):
            j = i+1
            if i == self.n-1 :
                j = 0

            a = np.array( [[self.x[i], 1.] , [self.x[j],1.]]  )
            b = np.array( [ self.y[i], self.y[j] ]  )
            c = np.linalg.solve(a,b)
            #print(' [%.3f , %.3f] = [ %.3f , %.3f ] [ %.3f, %.3f ] ' %( self.y[i], self.y[j], self.x[i], self.x[j], c[0], c[1] ) )
            self.m.append( c[0] )
            self.d.append( c[1] )


    # Solve n tips of the polygram from the polygon
    def GetPolygram(self):

        for i in range(self.n):
            j = i+2
            if j > self.n-1:
                j = j - self.n

            a = np.array( [[self.m[i], -1.] , [self.m[j],-1.]]  )
            b = np.array( [ -1*self.d[i], -1*self.d[j] ]  )
            c = np.linalg.solve(a,b)
            self.xt.append( c[0] )
            self.yt.append( c[1] )
            #print( '(%d,%d) = [ %.3f, %.3f ]' %( i, j, c[0], c[1]) )
            self.u.append( c[0] )
            self.v.append( c[1] )
            self.u.append( self.x[j] )
            self.v.append( self.y[j] )

        # Return to starting point
        self.u.append(self.xt[0])
        self.v.append(self.yt[0])

    def Create(self, n_, r_,  delta_ = -1.*math.pi /2 ):
        print( ' Create %d-side Polygram with radius %.2f' %( n_ , r_) )
        self.SetParameters( n_, r_, delta_ )
        self.GetPolygon()
        self.GetLine()
        self.GetPolygram()

    # rS status ->  2 : print , 1: move only , 0: retract,
    # This function is only used after Create
    def GetResult(self, rS = [], rx = [], ry = [], rz = [], zVal = 0., rE = [] ):

        eVal = 0
        for i in range( len(self.u) ):

            if i == 0:
                eVal = 0

                if len(rx) > 0:
                    rx.append( rx[ len(rx) -1 ] )
                    ry.append( ry[ len(ry) -1 ] )
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 0 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 1 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 0 )
                else :
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 1 )


            else :

                dx = self.u[i] - self.u[i-1]
                dy = self.v[i] - self.v[i-1]
                dl = math.sqrt( (dx*dx) + (dy*dy) )
                dt = dl / self.Fval
                eVal = self.Eval * dt

                rx.append(self.u[i])
                ry.append(self.v[i])
                rz.append( zVal )
                rE.append( eVal )
                rS.append( 2 )

    def Configure(self):

        self.n   = input('Number of Sides (5): ')
        if self.n   == '':  self.n = 5
        else :         self.n = int(self.n)
        self.r1    = input('1st Radius (15): ')
        if self.r1 == '':  self.r1 = 15
        else :         self.r1 = float( self.r1)
        self.r2    = input('2nd Radius (12): ')
        if self.r2 == '':  self.r2 = 12
        else :         self.r2 = float( self.r2)
        self.bw     = input('Bead width (0.5): ')
        if self.bw  == '':  self.bw = 0.5
        else :         self.bw = float(self.bw)
        self.h      = input('Height (1): ')
        if self.h  == '':  self.h = 1.0
        else :        self.h = float( self.h )
        self.delta = input(' Delta angle :')
        if self.delta == '' :  self.delta = -1*math.pi/2
        else :        self.delta  = float( self.delta )

        # Bead Height
        self.bh = 1.0

        self.nStep = int( abs(self.r1 - self.r2)/self.bw )
        self.nLayer = int( self.h / self.bh )

    def Construct2D(self, rs= [], rx= [], ry= [] ):

        # Rotation angle
        dtheta = 2*math.pi/ self.n

        # Inside-out or outside-in
        dr = self.bw
        r = self.r1 + (self.bw/2)
        if (self.r1 - self.r2) > 0 :
            r = self.r1 - (self.bw/2)
            dr = -1*self.bw

        da_ = self.delta
        for i in range( self.nStep ):
            #print( ' == r = %.3f == \n' %(r))
            self.Create( self.n, r , da_ )
            self.GetResult(rs, rx, ry)
            r = r+ dr
            #da_ = da_ + dtheta

    def Construct3D(self, rS=[], rx =[], ry= [], rz =[], rE = [] ):

        # Rotation angle
        dtheta = 2*math.pi/ self.n

        # Inside-out or outside-in
        dr = self.bw
        r = self.r1 + (self.bw/2)
        if (self.r1 - self.r2) > 0 :
            r = self.r1 - (self.bw/2)
            dr = -1*self.bw
        r0 = r
        stagger = 0.5*self.bw

        # Z level
        zVal = 0.

        # Starting angle
        da_ = self.delta
        for i in range( self.nLayer ):
            print(' Print Level %d' %(i))
            if i%2 == 1 :
                r = r0 + stagger*pow(-1,i)
            else :
                r = r0

            for j in range( self.nStep ):
                print( ' == r = %.3f == \n' %(r))
                self.Create( self.n, r , da_ )
                self.GetResult(rS, rx, ry, rz, zVal, rE  )
                r = r+ dr

            da_ = da_ + dtheta
            zVal = zVal + self.bh

rs = []
rx = []
ry = []
rz = []
rE = []
polyObj = Polygrams()
polyObj.Configure()
#polyObj.Construct2D(rs, rx, ry)
polyObj.Construct3D(rs, rx, ry, rz, rE )


# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Polygram', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([-55, 55])
plt.ylim([-55, 55])
plt.grid(b=True, which='major')
ax.scatter( polyObj.x,  polyObj.y,  s=50, marker= 'o', facecolors='none', edgecolors='red' )
ax.scatter( polyObj.xt, polyObj.yt, s=50, marker= '^', facecolors='none', edgecolors='blue' )

# Start Routing (x,y) -> (xt,yt) -> (x,y)
x_ = rx[0]
y_ = ry[0]
nPoint = len( rx )
print( ' total point %d ' %( len(rx)) )
n = polyObj.n
for i in range( nPoint -1 ) :
    dX = rx[i+1] - x_
    dY = ry[i+1] - y_
    # print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
    if i == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=5)
    #elif (i%(n*2+1) ) == (n*2):
    elif rs[i+1] == 1:
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='red', picker=5)
    elif rs[i+1] == 2 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='purple', picker=5)
    else :
        continue

    x_ = rx[i+1]
    y_ = ry[i+1]

plt.show()



