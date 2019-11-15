import matplotlib.pyplot as plt
import math
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from AreaFill import AreaFill
from Polygram import Polygrams

# Get basic 8 printing parameters
rcp = ReadRecipe('formNext_rcp_Ring2a.txt')
rcp.getPrintable()

x= []
y= []

# containers for printing path
rs = []
rx = []
ry = []
rz = []
rE = []

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
#polyObj.setGeometry(ri, ro, 72, math.pi, 0)
polyObj.setGeometry(ri, ro, 72, 2.13, 0)
polyObj.setRetraction(5,-1)

# 2. Basics for the Grids

# Grid printing configuration
dL = rcp.getParameter('dL')
ds = rcp.getParameter('ds')
dr = ds + dL
rc = ri - (rcp.bs)

#yspacing_scale = 0.5
#polychain.setArcSpacing( yspacing_scale)

# Number of turn at upper and lower polygon
n_up = int ( rcp.getParameter('N_up') )
n_low = int ( rcp.getParameter('N_low') )
# Height of the print
nSlice = int(rcp.nLayer)
yscale = rcp.getParameter('YScale')
# Arc spacing - bead spacing between adjacent line
arcspacing = rcp.getParameter('ArcSpacing')


# to set up initial y position
delta = ds*1.1

# Start constructing
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
rl = ri - (rcp.bs/2)
#clV = cl.polygonFillCircle( xc, yc, rc, delta, n_up, n_low, ds, dL, arcspacing )
clV = cl.polygonFillCircle( xc, yc, rc, delta, n_up, n_low, ds, dL, 2 )
print(' dL = %.3f , ds = %.3f ' %(dL, ds))

#dd = polychain.beadwidth*yspacing_scale*2
#rr = math.sqrt( pow((x1 -xc),2) + pow((y1-yc),2) )
#sAng = math.acos( (x1-xc)/rr)
#print('start angle is %.3f' %(sAng) )


###############################
# Start construct each layer  #
###############################

z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh
zz = z0
# Add skirt of the circle
#polyObj.AddSkirt(rs, rx, ry, rz, rE )

for i in range( nSlice ) :

    # Circle
    #polyObj.Construct2D(zz, rs, rx, ry, rz, rE, True )
    # Polygon Fill
    cl.getResult(clV, zz, rs, rx, ry, rz, rE, True)
    print( ' z = %.3f ' %( zz ))

    #if nSlice == 3 :
    #    dz = dz + 0.1
    zz = zz + dz

gc = GCodeGenerator( rs, rx, ry, rz, rE, rcp.Fval, rcp.rho )
gc.setMixingRatio( rcp.index )
gc.initTool()
gc.SetGlideSpeed( 300, 300 )
# Setup gliding time and eRatio for incoming and outgoing of an angle
gc.Gliding( 0.2, 0.1 , 0.2, 0.2, rs, rx, ry, rz, rE )
gc.Generate()
gc.EndingGCode()

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Polygon Test', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([5, 125])
plt.ylim([5, 125])
plt.grid(b=True, which='major')
ax.scatter( x,  y,  s=50, marker= 'o', facecolors='red', edgecolors='red' )

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