import math
import numpy as np
import matplotlib.pyplot as plt

from GCodeGenerator import GCodeGenerator

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

    # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh)
    bh = 0.5
    ts = 0.35
    fh = 0.1

    # Linear density ( or Flow rate )
    rho = 0.5
    Fval = 4000.
    Eval = Fval*rho

    def __init__(self, n_ = 5 ,  r_ = 10 ):
        self.n = int(n_)
        self.r = float(r_)
        self.delta = -1.*math.pi / 2
        self.theta = 2.*math.pi / self.n
        self.Eval = self.rho * self.Fval

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

        if self.objType == 0 :
            self.x.append( self.x[0] )
            self.y.append( self.y[0] )


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
        if self.objType == 1 :
            self.GetLine()
            self.GetPolygram()

    # status is given by the way(G0 or G1 or retract)  to the point
    # rS status ->  1 : print , 0: move only , 2: retract,
    # This function is only used after Create
    def GetPolygramResult(self, rS = [], rx = [], ry = [], rz = [], zVal = 0., rE = [] ):

        eVal = 0
        for i in range( len(self.u) ):

            if i == 0:
                eVal = -1.

                if len(rx) > 0:
                    rx.append( rx[ len(rx) -1 ] )
                    ry.append( ry[ len(ry) -1 ] )
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 2 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 0 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 2 )
                else :
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 0 )


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
                rS.append( 1 )

    def GetPolygonResult(self, rS = [], rx = [], ry = [], rz = [], zVal = 0., rE = [] ):

        eVal = 0
        for i in range( len(self.x) ):

            if i == 0:
                eVal = -1.

                if len(rx) > 0:
                    rx.append( rx[ len(rx) -1 ] )
                    ry.append( ry[ len(ry) -1 ] )
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 2 )
                    rx.append(self.x[i])
                    ry.append(self.y[i])
                    rz.append( zVal + 2 )
                    rE.append( eVal )
                    rS.append( 0 )
                    rx.append(self.x[i])
                    ry.append(self.y[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 2 )
                else :
                    rx.append(self.x[i])
                    ry.append(self.y[i])
                    rz.append( zVal )
                    rE.append( eVal )
                    rS.append( 0 )


            else :

                dx = self.x[i] - self.x[i-1]
                dy = self.y[i] - self.y[i-1]
                dl = math.sqrt( (dx*dx) + (dy*dy) )
                dt = dl / self.Fval
                eVal = self.Eval * dt

                rx.append(self.x[i])
                ry.append(self.y[i])
                rz.append( zVal )
                rE.append( eVal )
                rS.append( 1 )

    def GetResult(self, rs = [], rx = [], ry = [], rz = [], zVal = 0., rE = [] ):

        if self.objType == 0 :
            self.GetPolygonResult( rs, rx, ry, rz, zVal, rE )
        elif self.objType == 1 :
            self.GetPolygramResult( rs, rx, ry, rz, zVal, rE )
        else :
            self.GetPolygramResult( rs, rx, ry, rz, zVal, rE )


    def Configure(self):

        self.objType   = input('Polygon (0) or Polygram(1) : ')
        if self.objType   == '':  self.objType = 1
        else :         self.objType = int(self.objType)

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
        self.nLayer    = input('Number of Layer (1): ')
        if self.nLayer  == '':  self.nLayer = 1
        else :        self.nLayer = int( self.nLayer )
        self.delta = input(' Delta angle :')
        if self.delta == '' :  self.delta = -1*math.pi/2
        else :        self.delta  = float( self.delta )
        self.rho  = input(' Flow Rate (1.0) :')
        if self.rho == '' :  self.rho = 1.
        else :        self.rho  = float( self.rho )
        self.Fval  = input(' Stage Velocity (4800) :')
        if self.Fval == '' :  self.Fval = 4800
        else :        self.Fval  = float( self.Fval )

        self.Eval = self.rho * self.Fval
        self.nStep = int( abs(self.r1 - self.r2)/self.bw )
        print(" FlowRate %.3f Speed %.3f Extrude %.3f " %(self.rho, self.Fval, self.Eval ))

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
        #stagger = 0.5*self.bw
        stagger = 0

        # Z level
        zVal = self.bh + self.ts + self.fh

        # Starting angle
        da_ = self.delta
        for i in range( self.nLayer ):
            print(' Print Level %d' %(i))
            if dr > 0  and i%2 == 1 :
                r = r0 + stagger
            elif dr < 0  and i%2 == 1 :
                r = r0 - stagger
            else :
                r = r0

            for j in range( self.nStep ):
                print( ' == r = %.3f == \n' %(r))
                self.Create( self.n, r , da_ )
                self.GetResult(rS, rx, ry, rz, zVal, rE  )
                r = r+ dr
                da_ = da_ + dtheta

            zVal = zVal + self.bh

    def AddSkirt(self,rs = [], rx = [] , ry = [] , rz = [], rE = [] ) :

        rSkirt = max([self.r1, self.r2]) + 10
        print( ' == Printing Skirt %.3f==' %(rSkirt))

        # Starting angle
        da_ = self.delta
        # initial Z position
        zVal = self.bh + self.ts + self.fh

        self.Create( self.n, rSkirt, da_ )
        self.GetResult(rs, rx, ry, rz, zVal, rE  )





rs = []
rx = []
ry = []
rz = []
rE = []
polyObj = Polygrams()
polyObj.Configure()
#polyObj.Construct2D(rs, rx, ry)
polyObj.AddSkirt(rs, rx, ry, rz, rE )
polyObj.Construct3D(rs, rx, ry, rz, rE )

# Output GCode
gc = GCodeGenerator( rs, rx, ry, rz, rE, polyObj.Fval )
gc.Shift( 150, 150, 0 )
gc.Generate()

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
#ax.scatter( polyObj.xt, polyObj.yt, s=50, marker= '^', facecolors='none', edgecolors='blue' )

# Start Routing (x,y) -> (xt,yt) -> (x,y)
print( ' total point %d ' %( len(rx)) )
x_ = rx[0]
y_ = ry[0]
nPoint = len( rx )
n = polyObj.n
for i in range( nPoint -1 ) :
    dX = rx[i+1] - x_
    dY = ry[i+1] - y_
    # print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
    if i == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=5)
    #elif (i%(n*2+1) ) == (n*2):
    elif rs[i+1] == 0:
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='red', picker=5)
    elif rs[i+1] == 1 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='purple', picker=5)
    else :
        continue

    x_ = rx[i+1]
    y_ = ry[i+1]

plt.show()



