import math
import numpy as np
import matplotlib.pyplot as plt

from GCodeGenerator import GCodeGenerator

# Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
#    y = mx + d
#  |y1| = | x1  1 | | m |
#  |y2|   | x2  1 | | d |
#   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
def SolveLine( x1, y1, x2, y2 ) :
    a = np.array( [[ x1, 1.] , [ x2, 1.]]  )
    b = np.array( [y1, y2 ]  )
    c = np.linalg.solve(a,b)

    return c

# Return acos ( 0 ~ pi )
def dTheta( x1, y1, x2, y2, x3, y3 ) :

    a = [x2-x1, y2-y1, 0.]
    b = [x3-x2, y3-y2, 0.]
    ab  = np.inner(a,b)
    al = math.sqrt( (a[0]*a[0]) + (a[1]*a[1])  )
    bl = math.sqrt( (b[0]*b[0]) + (b[1]*b[1])  )
    cosA = ab/(al*bl)
    angle = math.acos( cosA*0.99999 )
    #print( ' cosA = %.3f , A = %.3f - %.3f' %(cosA, angle, angle*180/3.1415926 ) )

    return angle


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
    # solve m and d given (x1, y1) , (x2, y2)
    #  |y1| = | x1  1 | | m |
    #  |y2|   | x2  1 | | d |
    #   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
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

    def Gliding(self, eRatio , rS = [], rx = [], ry = [], rz = [], rE = [] ):

        # gd: Gliding distance (mm) : Def by  0.25 sec in whatever speed ( mm/sec )
        gd1 = 0.02 * self.Fval/60.
        gd2 = 0.02 * self.Fval/60.

        eVal1 = self.Eval*0.02*eRatio
        eVal2 = self.Eval*0.02*eRatio

        skipNext = False
        doGlide = False
        i = 0
        for iZ in rz :

            if skipNext :
                i=i+1
                skipNext = False
                continue

            if i > len(rE) -3 :
                doGlide = False
                break

            # Check the angle to see if gliding is necessary
            angle = dTheta( rx[i], ry[i], rx[i+1], ry[i+1], rx[i+2], ry[i+2] )
            if abs(angle) > 1.57 :
                doGlide = True


            if doGlide :
                # Calculate the segment length
                md1 = SolveLine( rx[i], ry[i], rx[i+1], ry[i+1] )
                dx1 = rx[i+1] - rx[i]
                dy1 = ry[i+1] - ry[i]
                L1 = math.sqrt( (dx1*dx1) + (dy1*dy1) )

                md2 = SolveLine( rx[i+1], ry[i+1], rx[i+2], ry[i+2] )
                dx2 = rx[i+2] - rx[i+1]
                dy2 = ry[i+2] - ry[i+1]
                L2 = math.sqrt( (dx2*dx2) + (dy2*dy2) )

                # Break the segment
                # Slow down/turn off
                if gd1 < L1 :
                    # adding another point
                    lx = dx1*gd1/L1
                    ly = dy1*gd1/L1
                    gx1 = rx[i+1] - lx
                    gy1 = ry[i+1] - ly
                    rx.insert( i+1, gx1 )
                    ry.insert( i+1, gy1 )
                    rz.insert( i+1, rz[i] )
                    rE.insert( i+1, rE[i] )
                    rS.insert( i+1, 1 )
                    rE[i+2] = eVal1
                    skipNext = True

                    # Turn back on
                    if gd2 < L2 :
                        lx2 = dx2*gd2/L2
                        ly2 = dy2*gd2/L2
                        gx2 = rx[i+2] + lx2
                        gy2 = ry[i+2] + ly2
                        rx.insert( i+3, gx2 )
                        ry.insert( i+3, gy2 )
                        rz.insert( i+3, rz[i] )
                        rE.insert( i+3, eVal2 )
                        rS.insert( i+3, 1 )
                        skipNext = True
                    #else :
                        rE[i+3] = rE[i+3]

                else :
                    # Turn off at next point
                    rE[i+1] = rE[i+1]
                    # Turn back on
                    if gd2 < L2 :
                        lx2 = dx2*gd2/L2
                        ly2 = dy2*gd2/L2
                        gx2 = rx[i+1] + lx2
                        gy2 = ry[i+1] + ly2
                        rx.insert( i+2, gx2 )
                        ry.insert( i+2, gy2 )
                        rz.insert( i+2, rz[i] )
                        rE.insert( i+2, eVal2 )
                        rS.insert( i+2, 1 )
                        skipNext = True
                    else :
                        rE[i+2] =  rE[i+2]

            doGlide = False
            i = i+1



    # status is given by the way(G0 or G1 or retract)  to the point
    # rS status ->  1 : print , 0: move only , 2: retract,
    # This function is only used after Create
    def GetPolygramResult(self, rS = [], rx = [], ry = [], rz = [], zVal = 0., rE = [], retract = False ):

        eVal = 0
        for i in range( len(self.u) ):

            if i == 0:
                eVal = -1.

                # Adding retraction
                if len(rx) > 0 and retract :
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
                    rE.append( 0.0 )
                    rS.append( 2 )
                else :
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append( zVal )
                    rE.append( 0.0 )
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

    def GetPolygonResult(self, rS = [], rx = [], ry = [], rz = [], zVal = 0., rE = [], retract = False ):

        eVal = 0
        for i in range( len(self.x) ):

            if i == 0:
                eVal = -1.

                if len(rx) > 0 and retract :
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
                    rE.append( 0.0 )
                    rS.append( 2 )
                else :
                    rx.append(self.x[i])
                    ry.append(self.y[i])
                    rz.append( zVal )
                    rE.append( 0.0 )
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

    def GetResult(self, rs = [], rx = [], ry = [], rz = [], zVal = 0., rE = [], retract = False ):

        if self.objType == 0 :
            self.GetPolygonResult( rs, rx, ry, rz, zVal, rE, retract )
        elif self.objType == 1 :
            self.GetPolygramResult( rs, rx, ry, rz, zVal, rE, retract )
            self.Gliding( 0.0, rs, rx, ry, rz, rE)
        else :
            self.GetPolygramResult( rs, rx, ry, rz, zVal, rE, retract )
            self.Gliding( 0.0, rs, rx, ry, rz, rE)


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
                if j == 0 :
                    retract = True
                else :
                    retract = False
                self.Create( self.n, r , da_ )
                self.GetResult(rS, rx, ry, rz, zVal, rE, retract   )
                r = r+ dr

            '''
            hNS = 0
            if self.nStep%2 == 0 :
                hNS = int( self.nStep /2 )
            if self.nStep%2 == 1 :
                hNS = int( self.nStep /2) + 1
            print( 'Number of step : %d' %(hNS) )

            for j in range( hNS ):
                r = r0 + (j*dr)
                print( ' ==(%d) r1 = %.3f == \n' %(j, r))
                self.Create( self.n, r , da_ )
                self.GetResult(rS, rx, ry, rz, zVal, rE  )

                k = self.nStep - 1 - j
                if k == j :
                    continue
                else :
                    r = r0 + (k*dr)
                    print( ' ==(%d) r2 = %.3f == \n' %(k, r))
                    self.Create( self.n, r , da_ )
                    self.GetResult(rS, rx, ry, rz, zVal, rE  )

            '''

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



