from Quadrilateral import Rectangle
from ReadRecipe import ReadRecipe
from GCodeGenerator import GCodeGenerator
import matplotlib.pyplot as plt
from AreaFill import AreaFill

# Get basic 8 printing parameters
rcp = ReadRecipe('mueller_rcp.txt')
# Get all printing parameters from the recipe file
rcp.getPrintable()
index = rcp.getParameter('Index')
length = rcp.getParameter('Length')
width = rcp.getParameter('Width')
angle = rcp.getParameter('Angle')
x0 = rcp.getParameter('InitX')
y0 = rcp.getParameter('InitY')
BSScale = rcp.getParameter('BSScale')

rx = []
ry = []
rz = []
rE = []
rS = []

recObj = Rectangle( length, width , 1, angle )
recObj.Setup( length, width, angle, int(rcp.nLayer), x0, y0 )
recObj.SetPrintable( rcp.Fval, rcp.rho, rcp.bh, rcp.ts, rcp.fh, rcp.bs, rcp.rh, rcp.nLayer )
recObj.FillingSetup( True, BSScale, BSScale, False )
recObj.Construct3D( rx, ry, rz, rE, rS )

recObj.Setup( length, width, angle, int(rcp.nLayer), x0+12.5, y0 )
recObj.SetPrintable( rcp.Fval, rcp.rho, rcp.bh, rcp.ts, 1.0, rcp.bs, rcp.rh, rcp.nLayer )
recObj.FillingSetup( True, BSScale, BSScale, True )
recObj.Construct3D( rx, ry, rz, rE, rS )

# Grid printing configuration
glength = rcp.getParameter('GLength')
gwidth = rcp.getParameter('GWidth')
gx0 = rcp.getParameter('GInitX')
gy0 = rcp.getParameter('GInitY')
gBSScale = rcp.getParameter('GBSScale')
recObj1 = Rectangle( glength, gwidth , 1, angle )
recObj1.Setup( glength, gwidth, angle, 1, gx0, gy0 )
shapeV = recObj1.GetShape()
shellV = recObj1.GetSkirt( -1*rcp.bs*gBSScale )

dL = rcp.getParameter('dL')
ds = rcp.getParameter('ds')
# Number of turn at upper and lower polygon
n_up = int ( rcp.getParameter('N_up') )
n_low = int ( rcp.getParameter('N_low') )
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
cl.setBeadSpacing( rcp.bs, gBSScale )
psx = rcp.getParameter('Partition_dX')
psy = rcp.getParameter('Partition_dY')
cl.shiftPartition( psx , psy )
arcV = cl.FillArbitrary( shellV, ds, dL, n_up, n_low )

# add additional side (top edge)
#edgeV = []
#edgeV.append( [220, 69.75] )
#edgeV.append( [24.5, 69.75] )
#edgeV.append( [24.5, 64.5] )

# Add shell for grid pattern
#cl.getResult(shapeV, zz, rs, rx, ry, rz, rE, True)

nGLayer = rcp.getParameter('N_GridLayer')
zz = (rcp.bh*(rcp.nLayer+1)) + rcp.ts + rcp.fh
for i in range( int(nGLayer) ) :

    cl.getResult(shapeV, zz, rS, rx, ry, rz, rE, True)
    #cl.getResult(shellV, zz, rS, rx, ry, rz, rE, True)
    cl.getResult(arcV, zz, rS, rx, ry, rz, rE, True)
    zz = zz + rcp.bh

# Output GCode
gc = GCodeGenerator( rS, rx, ry, rz, rE, rcp.Fval, rcp.rho )
gc.setMixingRatio( index )
gc.initTool()
#gc.tipWipe(30, 50, 100 )
#gc.SetGlideSpeed( 300, 300 )
# Setup gliding time and eRatio for incoming and outgoing of an angle
#gc.Gliding( 0.2, 0.5 , 0.2, 0.5, rS, rx, ry, rz, rE )
#gc.Shift( 100, 100, 0 )
gc.Generate()

gc.EndingGCode()

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Rectangle', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([0, 330])
plt.ylim([0, 330])
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
