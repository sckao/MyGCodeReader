import math
import matplotlib.pyplot as plt
from GCodeGenerator import GCodeGenerator, Ending
from ReadRecipe import ReadRecipe
from Polygram import Polygrams
from AreaFill import AreaFill

# Get basic 8 printing parameters
rcp = ReadRecipe('formNext_rcp_Ring3.txt')
rcp.getPrintable()
nSlice = int(rcp.nLayer)

rx = []
ry = []
rz = []
rE = []
rs = []

# 1. Setup the outer ring
# Basics for the ring configuration
polyObj = Polygrams()
polyObj.setPrintable( rcp.Fval, rcp.rho, rcp.bh, rcp.ts, rcp.fh, rcp.bs, rcp.nLayer )
# center of circle, inner and outer radius
xc = rcp.getParameter('CenterX')
yc = rcp.getParameter('CenterY')
ri = rcp.getParameter('InnerR')
ro = rcp.getParameter('OuterR')
polyObj.setCenter(xc, yc)
polyObj.setGeometry(ri, ro, 72, 1.974, 0)
# retraction distance 5 mm , Eval = -1
polyObj.setRetraction(rcp.rh,-1)


# 2. Zigzag Filling
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
rl = ri - rcp.bs
clV = cl.LineFillCircle(xc, yc, rl, 2*rcp.bs )

ang = math.acos( (rl-(2*rcp.bs))/rl )
print(' start angle = %.3f' %(ang + (math.pi/2)) )
###############################
# Start construct each layer  #
###############################

z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh
zz = z0
# Add skirt of the circle
#polyObj.AddSkirt(rs, rx, ry, rz, rE )
for i in range( nSlice ) :

    # 1.  Circle
    polyObj.Construct2D(zz, rs, rx, ry, rz, rE, True )
    # 2. Zigzag Fill
    cl.getResult( clV, zz, rs, rx, ry, rz, rE, True )

    Ending( 2, rs, rx, ry, rz, rE )


    print( ' z = %.3f ' %( zz ))
    zz = zz + dz


# Output GCode
gc = GCodeGenerator( rs, rx, ry, rz, rE, rcp.Fval, rcp.rho )

gc.SetGlideSpeed( 300, 300 )
# Setup gliding time and eRatio for incoming and outgoing of an angle
gc.Gliding( 0.4, 0.1 , 0.4, 0.1, rs, rx, ry, rz, rE )

#gc.Shift( 0, 0, 0 )

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
    elif abs(rs[i+1]) == 2 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='blue', picker=5)
    elif rs[i+1] == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='black', picker=5)
    else :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='purple', picker=5)

    x_ = rx[i+1]
    y_ = ry[i+1]

plt.show()
