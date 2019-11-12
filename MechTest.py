from Quadrilateral import Rectangle
from ReadRecipe import ReadRecipe
from GCodeGenerator import GCodeGenerator
import matplotlib.pyplot as plt

# Get basic 8 printing parameters
rcp = ReadRecipe('mechtest_rcp_prep1.txt')
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
recObj.FillingSetup( True, BSScale, BSScale)
recObj.Construct3D( rx, ry, rz, rE, rS )

# Output GCode
gc = GCodeGenerator( rS, rx, ry, rz, rE, rcp.Fval, rcp.rho )
gc.setMixingRatio( index )
gc.SetGlideSpeed( 300, 300 )
# Setup gliding time and eRatio for incoming and outgoing of an angle
gc.Gliding( 0.2, 0.5 , 0.2, 0.5, rS, rx, ry, rz, rE )

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
