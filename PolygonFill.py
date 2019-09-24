import math
import numpy as np
import matplotlib.pyplot as plt
from GCodeGenerator import GCodeGenerator

def sortX( vec ):
    return vec[0]

def sortY( vec ):
    return vec[1]

class PolygonFill:

    # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh)
    bh = 0.5
    ts = 0.35
    fh = 0.1

    # Linear density ( or Flow rate )
    rho = 0.75
    Fval = 6000.
    Eval = Fval*rho


    def __init__( self ):

        # n must be >=  3
        self.pos = []
        self.beadwidth = 0.75
        self.u = []
        self.v = []
        self.z = []
        self.s = []



    def getResult(self, pos= [], xlist=[], ylist=[], z=0, s=1 ):


        for i in range( len(pos)) :

            xlist.append( pos[i][0] )
            ylist.append( pos[i][1] )
            self.u.append( pos[i][0] )
            self.v.append( pos[i][1] )
            self.z.append( z )
            self.s.append( s )

    def reset(self):

        self.u = []
        self.v = []
        self.z = []
        self.s = []


    def getData4Gcode(self, rx=[], ry=[], rz=[],rs=[], rE=[], retract = False ):

        eVal = 0
        for i in range(len(self.s)) :

            if i == 0:
                eVal = -1.

                # Adding retraction
                if len(rx) > 0 and retract :
                    rx.append( rx[ -1 ] )
                    ry.append( ry[ -1 ] )
                    rz.append( rz[ -1 ] + 2 )
                    rE.append( eVal )
                    rs.append( 2 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(self.z[-1] + 2 )
                    rE.append( eVal )
                    rs.append( 0 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(self.z[i] )
                    rE.append( 0.1 )
                    rs.append( -2 )
                else :
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(self.z[i] )
                    rE.append( 0.0 )
                    rs.append( 0 )

            else :
                dx = self.u[i] - self.u[i-1]
                dy = self.v[i] - self.v[i-1]
                dl = math.sqrt( (dx*dx) + (dy*dy) )
                dt = dl / self.Fval
                eVal = self.Eval * dt

                rx.append(self.u[i])
                ry.append(self.v[i])
                rz.append(self.z[i] )
                rE.append( eVal )
                rs.append( 1 )


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
    # x0,y0 :  starting position
    # Lx : length of the polygon chain
    # ds : diameter of the polygon, dL : spacing between polygons
    # n,m : number of points in upper or lower arch
    def createChain(self,x0,y0, Lx, ds, dL, n, m, k = 1 ):

        # Setup parameters
        i = 1
        arcs = []
        d = self.beadwidth
        angle1 = math.pi/((n+1)*2)
        angle2 = math.pi/((m+1)*2)
        cor =  (d/math.cos(angle1)) - (d*math.tan(angle1))

        # start routing
        # adding the first segment
        x = x0
        y = y0 + ((k-1)*d)
        h1 = 0
        arcs.append([x,y])
        x = x0 + dL - ((k-1)*cor)
        y = y0 + ((k-1)*d)
        arcs.append([x,y])

        # used for constructing arc
        xc = x0 + dL + (ds/2)
        yc = y0
        while  Lx >= (ds+dL)*i :

            # radius to construct the polygon
            r = ds + ((k-1)*d*2/math.cos(angle1))

            print(" (%d) xc,yc,r =  %.3f, %.3f , %.3f" %(i, xc,yc, r))
            h1 = self.createArc( xc, yc, r, n, arcs )
            if (ds+dL)*(i+1) <= Lx :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                x = arcs[-1][0] + dL - ((k-1)*cor*2)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
            else :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                x = arcs[-1][0] + dL - ((k-1)*cor) + ((k-1)*d)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )

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
                x = x - ds - ((k-1)*cor*2)
                y = y0 -d - ((k-1)*d)
                arcs.append( [x, y] )

                x = x - dL + ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d)
                arcs.append( [x, y] )
            else :
                x = x  - ds - ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d)
                arcs.append( [x, y] )

            xc = xc - dL - ds
            i = i-1
            j = j+1

        x = x -dL + ((k-1)*cor)
        y = y
        arcs.append([x,y])
        print( ' ** End at  xy = (%.3f , %.3f)' %( x, y))
        h = h1+h2
        return arcs, h

    def unitSize(self, ds, dL, n, m, k = 1):
        arcs, h = self.createChain( 0, 0,dL+ds, ds, dL, n, m, k)
        width = ds
        height = h + self.beadwidth
        return width, height


    def FillAreaN(self, xV, yV, LV, ds, dL, n, m, k = 1, z = 0 ):

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
                    self.getResult( arc, x,y, z, 0)
                elif xV[i] < iniX :
                    arc = []
                    iniY = y[-1]
                    arc.append( [ xV[i], iniY])
                    self.getResult( arc, x,y, z, 0)
                else :
                    arc = []
                    arc.append( [ xV[i], yV[i]])
                    self.getResult( arc, x,y, z, 0)

                # Move to starting point of this row
                iniX = xV[i]
                iniY = yV[i]
                if i%2 == 0 :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, n, m, j)
                    self.getResult( arcs, x,y, z, 1)
                else :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, m, n, j)
                    self.getResult( arcs, x,y, z, 1)

        return x, y


    def addSkirt(self, x0, y0, LV, ds, dL, n, m, k, delta = 5 ):

        w0 , h0 = self.unitSize(ds,dL,n, m, k)
        print( 'Unit size = %.3f , %.3f' %(w0, h0))

        width = max(LV)
        height = len(LV)*h0

        self.u = []
        self.v = []

        # point 1
        x = x0 - delta
        y = y0 + delta
        self.u.append( x )
        self.v.append( y )

        # point2
        x = x + width + (2*delta)
        y = y
        self.u.append( x )
        self.v.append( y )

        # point3
        x = x
        y = y - height - (2*delta)
        self.u.append( x )
        self.v.append( y )

        # point4
        x = x - width - (2*delta)
        y = y
        self.u.append( x )
        self.v.append( y )

        # back to point1
        x = x
        y = y + height + (2*delta)
        self.u.append( x )
        self.v.append( y )

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

rs = []
rx = []
ry = []
rz = []
rE = []

polychain = PolygonFill()
iniX = 80
iniY = 80
n_up = 2
n_low = 2
ds = 10
dL = 5
nLayer = 2

LV = [90,60,90,60,90]
xV0 = [0,15,0,15,0]
yV = []
xV = []
w0 , h0 = polychain.unitSize(ds,dL,n_up, n_low, nLayer)

polychain.addSkirt(iniX, iniY, LV, ds, dL, n_up, n_low, nLayer, 10)
polychain.getData4Gcode(rx,ry,rz,rs,rE)

for i in range( len(LV) ):
    xV.append(iniX + xV0[i] )
    yV.append(iniY)
    iniY = iniY - h0 - ((polychain.beadwidth)*(2*nLayer -1 ))


z = 0.95
polychain.reset()
x, y = polychain.FillAreaN(xV, yV, LV, ds, dL, n_up, n_low, nLayer, z)
polychain.getData4Gcode(rx,ry,rz,rs,rE,True)

# Generate GCode
fVal = 6000

gc = GCodeGenerator( rs, rx, ry, rz, rE, fVal )
#gc.SetGlideSpeed( polyObj.gFval1, polyObj.gFval2 )
#gc.SetGlideSpeed( 2000, 3000 )
#gc.Gliding( 0.06, 0.1 , 0.06, 0.1, rs, rx, ry, rz, rE )
#gc.Shift( 150, 150, 0 )
gc.Generate()

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
plt.xlim([-5, 105])
plt.ylim([-5, 95])
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