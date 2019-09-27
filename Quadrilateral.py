import math
import matplotlib.pyplot as plt

from GCodeGenerator import GCodeGenerator
from GCodeGenerator import Ending
from GCodeGenerator import dLength

class Rectangle :

    width = 0
    length = 0
    height = 0
    phi= math.pi
    bw = 0.75
    bh = 0.5
    ts = 0.35
    fh = 0.1
    rd = 5.0 # retraction distance
    zOffset = 0. # addition Z height to offset the z0

    nLayer = 1

    # Linear density ( or Flow rate )
    rho = 1
    Fval = 2000.
    Eval = Fval*rho

    u = []
    v = []

    def __init__(self, l, w, h, angle ) :
        self.width = w
        self.length = l
        self.height = h
        self.phi    = angle
        self.shelled = False
        self.x0 = 0
        self.y0 = 0
        self.u = []
        self.v = []

    # phi : 0~ 2pi , angle of d-vector
    # d : travel distance in x, w: total width in y to fill
    # ud = -1 or 1 => go downward or upward
    def AddShell(self, ud = 1 ):

        d = self.length
        w = self.width
        phi = self.phi
        x = self.x0
        y = self.y0

        self.u.append( x )
        self.v.append( y )

        x = x + d*math.cos(phi)
        y = y + d*math.sin(phi)
        self.u.append( x )
        self.v.append( y )

        x = x
        y = y + (ud*w)
        self.u.append( x )
        self.v.append( y )


        x = x + d*math.cos( phi - math.pi )
        y = y + d*math.sin( phi - math.pi )
        self.u.append( x )
        self.v.append( y )

        self.u.append( self.x0 )
        self.v.append( self.y0 )

        self.shelled = True

    # ud : -1 for downward  , 1 for upward
    def AddSkirt(self, delta =20, ud = 1 ):

        phi = self.phi
        LR = 1
        if math.cos(phi) > 0 : LR =  1
        else :                 LR = -1

        dy = (delta/abs(math.cos(phi))) + LR*ud*(delta*abs(math.tan(phi)))
        d = self.length + (2*delta/abs(math.cos(phi)))
        w = self.width + (2*delta/abs(math.cos(phi)))
        x = self.x0 - (delta*LR)
        y = self.y0 - (ud*dy )

        x_0 = x
        y_0 = y

        self.u.append( x )
        self.v.append( y )

        x = x + d*math.cos(phi)
        y = y + d*math.sin(phi)
        self.u.append( x )
        self.v.append( y )

        x = x
        y = y + (ud*w)
        self.u.append( x )
        self.v.append( y )


        x = x + d*math.cos( phi - math.pi )
        y = y + d*math.sin( phi - math.pi )
        self.u.append( x )
        self.v.append( y )

        self.u.append( x_0 )
        self.v.append( y_0 )


    # phi : 0~ 2pi , angle of w-vector
    # d : travel distance in x, w: total width in y to fill
    # ud = 1 or -1 => go upward or downward
    def XZigzagFill(self, ud = 1, addY_bw = 0  ):

        phi = self.phi
        LR = 1
        if math.cos(phi) < 0 : LR =  -1

        ybw = self.bw + addY_bw
        dy = ( ybw /abs(math.cos(phi))) + LR*ud*(self.bw*abs(math.tan(phi)))

        d = self.length
        w = self.width
        x = self.x0
        y = self.y0

        # Take shell thickness into consideration
        if self.shelled :
            d = self.length - (2*self.bw/abs(math.cos(phi)))
            w = self.width - (2*ybw/abs(math.cos(phi)))
            x = self.x0 + (self.bw*LR)
            y = self.y0 + (ud*dy )

        i = 0.
        self.u.append( x )
        self.v.append( y )
        stepY = ybw/abs(math.cos(phi))
        while (w - (i*stepY) ) >= 0  :

            x = x + d*math.cos(phi)
            y = y + d*math.sin(phi)
            self.u.append( x )
            self.v.append( y )

            i = i + 1
            y = y + (ud*stepY )
            x = x
            phi = phi - ( math.pow(-1,i-1)*math.pi)
            if (w - (i*stepY)) >=0 :
                self.u.append( x )
                self.v.append( y )

    # phi : 0~ 2pi , angle of w-vector
    # d : travel distance in x, w: total width in y to fill
    # ud = -1 or 1 => go downward or upward
    def YZigzagFill(self, ud = 1, addX_bw = 0):

        phi = self.phi
        LR = 1
        if math.cos(phi) < 0 : LR =  -1
        dy = (self.bw/abs(math.cos(phi))) + LR*ud*(self.bw*abs(math.tan(phi)))

        d = self.length
        w = self.width
        x = self.x0
        y = self.y0
        xbw = self.bw + addX_bw
        if self.shelled :
            d = self.length - (2*xbw/abs(math.cos(phi)))
            w = self.width - (2*self.bw/abs(math.cos(phi)))
            x = self.x0 + (xbw*LR)
            y = self.y0 + (ud*dy )

        r = 0.
        if  phi == math.pi/2 or phi == 1.5*math.pi :
            return
        else :
            r = abs(xbw / math.cos( phi ))

        print( " step = %.5f " %(r) )

        i = 0.
        self.u.append( x )
        self.v.append( y )
        while (d - (i*r) ) >= 0  :

            x = x
            y = y + (pow(-1,i)*w*ud)
            self.u.append( x )
            self.v.append( y )

            i = i + 1
            x = x + r*math.cos(phi)
            y = y + r*math.sin(phi)
            if (d - (i*r)) >=0 :
                self.u.append( x )
                self.v.append( y )


    def GetResult(self, zVal = 0, rx = [], ry= [], rz = [], rE = [], rs= [], retract = True ):

        for i in range( len(self.u) ) :

            # Calculate Eval
            prime_eval = 0.1
            retract_eval = -1
            shift_eval = 0
            if i == 0 :

                if retract :
                    rx.append( self.u[i] )
                    ry.append( self.v[i] )
                    rz.append( zVal + self.rd )
                    rs.append( 0 )
                    rE.append( shift_eval )

                    rx.append( self.u[i] )
                    ry.append( self.v[i] )
                    rz.append( zVal )
                    rs.append( -2 )
                    rE.append( prime_eval  )
                else :
                    rx.append( self.u[i] )
                    ry.append( self.v[i] )
                    rz.append( zVal )
                    rs.append( 0 )
                    rE.append( shift_eval )


            else :
                dx = self.u[i] - self.u[i-1]
                dy = self.v[i] - self.v[i-1]
                dt = math.sqrt( (dx*dx)+ (dy*dy) ) / self.Fval
                eval = self.Eval * dt

                rx.append( self.u[i] )
                ry.append( self.v[i] )
                rz.append( zVal )
                rs.append( 1 )
                rE.append( eval )

            i = i+1

        if retract :
            rx.append( self.u[i-1] )
            ry.append( self.v[i-1] )
            rz.append( zVal + self.rd )
            rs.append( 2 )
            rE.append( retract_eval )

    def Construct3D(self, rx =[], ry= [], rz = [] , rE = [], rS = [] ):

        h = self.height

        i = 0
        z = self.ts + self.bh + self.fh
        self.AddSkirt( 20, 1 )
        self.GetResult( z, rx, ry, rz, rE, rS )
        self.u = []
        self.v = []
        #while h >= (i*self.bh ) :
        for i in range( self.nLayer ) :

            self.AddShell( 1 )
            self.GetResult( z, rx, ry, rz, rE, rS )
            self.u = []
            self.v = []
            print(' Layer %d = %.3f ' %(i,z ))
            if i%2 == 0 :
                self.XZigzagFill( 1 )
                self.GetResult( z, rx, ry, rz, rE, rS )
                self.u = []
                self.v = []
            else :
                self.YZigzagFill( 1 )
                self.GetResult( z, rx, ry, rz, rE, rS )
                self.u = []
                self.v = []

            z = z + self.bh

    def Setup(self, length, width, phi, nLayer, x0, y0 ):

        self.length = length
        self.width  = width
        self.phi    = phi
        self.nLayer = nLayer
        self.x0 = x0
        self.y0 = y0

    def ConstructBMW(self, rx =[], ry= [], rz = [] , rE = [], rS = [] ):

        h = self.height
        theX0 = 15
        theY0 = 87
        dY0   = 15

        i = 0
        #z = self.ts + self.bh + self.fh + 6.25
        z = self.ts + self.bh + self.fh
        self.Setup(127,54,0,1, theX0, theY0 )
        self.AddSkirt( 5, 1 )
        self.GetResult( z, rx, ry, rz, rE, rS )
        self.u = []
        self.v = []

        for i in range( self.nLayer ) :

            theY0 = 87
            for j in range(4) :

                self.Setup(127,9,0,1, theX0, theY0 )
                self.AddShell( 1 )
                self.GetResult( z, rx, ry, rz, rE, rS )
                self.u = []
                self.v = []
                print(' Layer %d = %.3f ' %(i,z ))
                if i%2 == 0 :
                    self.XZigzagFill( 1 )
                    self.GetResult( z, rx, ry, rz, rE, rS )
                    #
                    Ending( 7, rS,rx, ry, rz, rE )
                    self.u = []
                    self.v = []
                else :
                    self.YZigzagFill( 1 )
                    self.GetResult( z, rx, ry, rz, rE, rS )
                    self.u = []
                    self.v = []

                theY0 = theY0 + dY0

            z = z + self.bh

    def Configure(self):

        self.length = input('Length (80 mm): ')
        if self.length == '':
            self.length = 80
        else:
            self.length = float(self.length)

        self.width = input('Width (20 mm): ')
        if self.width == '':
            self.width = 20
        else:
            self.width = float(self.width)

        self.zOffset = input('Z Offset (0 mm): ')
        if self.zOffset == '':
            self.zOffset = 0
        else:
            self.zOffset = float(self.zOffset)

        self.phi = input(' Angle (0~ 2pi, default : 0) :')
        if self.phi == '':
            self.phi = 0
        else:
            self.phi = float(self.phi)
        self.bw = input('Bead width (0.75): ')
        if self.bw == '':
            self.bw = 0.75
        else:
            self.bw = float(self.bw)
        self.nLayer = input('Number of Layer (1): ')
        if self.nLayer == '':
            self.nLayer = 1
        else:
            self.nLayer = int(self.nLayer)

        self.x0 = input('Initial X Position (100): ')
        if self.x0 == '':
            self.x0 = 100.
        else:
            self.x0 = float(self.x0)
        self.y0 = input('Initial Y Position (100): ')
        if self.y0 == '':
            self.y0 = 100.
        else:
            self.y0 = float(self.y0)


    def CustomConstruction(self, rx =[], ry= [], rz = [] , rE = [], rS = [] ):

        self.Configure()
        retract = False

        i = 0
        z = self.ts + self.bh + self.fh + self.zOffset
        # 5 mm away from the edge
        self.AddSkirt( 5, 1 )
        self.GetResult( z, rx, ry, rz, rE, rS, retract )
        Ending( 1, rS,rx, ry, rz, rE )
        self.u = []
        self.v = []

        for i in range( self.nLayer ) :


            self.AddShell( 1 )
            #self.GetResult( z, rx, ry, rz, rE, rS, retract )
            #Ending( 0.5, rS,rx, ry, rz, rE )
            #self.u = []
            #self.v = []
            print(' Layer %d = %.3f ' %(i,z ))
            if i%2 == 2 :
                self.XZigzagFill( 1 )
                self.GetResult( z, rx, ry, rz, rE, rS )
                Ending( 10, rS,rx, ry, rz, rE )
                self.u = []
                self.v = []
            else :
                self.YZigzagFill( 1, self.bw*3 )
                self.GetResult( z, rx, ry, rz, rE, rS )
                #Ending( 0.5, rS,rx, ry, rz, rE )
                self.u = []
                self.v = []

            if i > 2 :
                z = z + self.bh + 0.1
            else :
                z = z + self.bh

        #Ending( 5, rS,rx, ry, rz, rE )



rx = []
ry = []
rz = []
rE = []
rS = []

recObj = Rectangle(20, 5 , 1, math.pi)
#recObj.ConstructBMW(rx, ry, rz, rE, rS)
recObj.CustomConstruction( rx, ry, rz, rE, rS )

# Output GCode
gc = GCodeGenerator( rS, rx, ry, rz, rE, recObj.Fval )

#gc.SetGlideSpeed( 2000, 3000 )
#gc.Gliding( 0.05, 0.1 , 0.05, 0.1, rS, rx, ry, rz, rE )

#gc.Shift( 100, 100, 0 )
gc.Generate()

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Rectangle', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([20, 200])
plt.ylim([20, 200])
plt.grid(b=True, which='major')

# Start Routing (x,y) -> (xt,yt) -> (x,y)
print( ' total point %d ' %( len(rx)) )
x_ = rx[0]
y_ = ry[0]
nPoint = len( rx )
for i in range( nPoint -1 ) :
    dX = rx[i+1] - x_
    dY = ry[i+1] - y_
    # print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
    if i == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=5)
    #elif (i%(n*2+1) ) == (n*2):
    elif i == nPoint -2 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='red', picker=5)
    elif abs(rS[i+1]) == 2 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='blue', picker=5)
    elif rS[i+1] == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='black', picker=5)
    else :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='purple', picker=5)

    x_ = rx[i+1]
    y_ = ry[i+1]

plt.show()

