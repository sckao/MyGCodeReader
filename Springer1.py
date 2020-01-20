import matplotlib.pyplot as plt
import math
from GWords import GWords
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from AreaFill import AreaFill
from ConcentricFill import ConcentricFill
from ModelMotion import *


def SplitOutline( outlnV, yCut ) :

    outlnU0 = []
    outlnD0 = []
    for i in range( len(outlnV) ) :

        if outlnV[i][1] >= yCut :
            outlnU0.append( [ outlnV[i][0], outlnV[i][1] ])
            if len(outlnD0) > 0 and outlnD0[-1] != [] :
                outlnD0.append( [] )
        else :
            outlnD0.append( [ outlnV[i][0], outlnV[i][1] ])
            if len(outlnU0) > 0 and outlnU0[-1] != [] :
                outlnU0.append( [] )

    outlnU01 = ReSort(outlnU0)
    outlnD01 = ReSort(outlnD0)
    del outlnU01[0]
    del outlnD01[0]
    #outlnU01.remove( [] )
    #outlnD01.remove( [] )

    return outlnU01, outlnD01


###################################################
#             Springer project code               #
###################################################

# Get basic 8 printing parameters
rcp = ReadRecipe('springer1_rcp.txt')
rcp.getPrintable()
BSScale = rcp.getParameter('BSScale')


x= []
y= []

# containers for printing path
rs = []
rx = []
ry = []
rz = []
rE = []

# 1. Makeup a shape for test
# Read a GCode Shape file
shapeV = ReadOutline( 'InsertOutline.gcode', -50, 200, -0.5*math.pi )
shapeV1 = ReadOutline( 'InsertOutline1.gcode', -50, 200, -0.5*math.pi )
shapeV2 = ReadOutline( 'InsertOutline2.gcode', -50, 200, -0.5*math.pi )

# 2. Get skirt of the print and outline of pattern2
cf = ConcentricFill()
skirtV = cf.GetOutline(shapeV, 5, True )
shapeV2a = cf.GetOutline(shapeV2, -1., False )

# 3. Setup Filling parameters
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
cl.setBeadSpacing( rcp.bs, BSScale)

# 4. Grid printing configuration
nGLayer = rcp.getParameter('GNLayer')
dL1 = rcp.getParameter('dL1')
ds1 = rcp.getParameter('ds1')
n1_up = int ( rcp.getParameter('N1_up') )
n1_low = int ( rcp.getParameter('N1_low') )

dL2 = rcp.getParameter('dL2')
ds2 = rcp.getParameter('ds2')
n2_up = int ( rcp.getParameter('N2_up') )
n2_low = int ( rcp.getParameter('N2_low') )


# 5. construct the fill around shape1 and shape2
# 5.1 Find the center Y
tB,bB,lB,rB = cl.defineRange( shapeV )
Yc = (tB[1] + bB[1]) /2
#xB0 = cl.findXBoundary( Yc , shapeV )
#xB1 = cl.findXBoundary( Yc , shapeV1 )
#xB2 = cl.findXBoundary( Yc , shapeV2 )
# 5.2 Divide shapeV , shapeV1 and shapeV2 to two halves ( U and D )
shapeU0, shapeD0 = SplitOutline( shapeV, Yc)
shapeU1, shapeD1 = SplitOutline( shapeV1, Yc)
shapeU2, shapeD2 = SplitOutline( shapeV2, Yc)
# 5.3 Combine half shapeV + shapeV1 and shapeV2 in the order
shapeU = shapeU0 + shapeU2 + shapeU1
shapeU.append( shapeU[0] )
shapeD = shapeD0 + shapeD1 + shapeD2
shapeD.append( shapeD[0] )

# 6. Start Filling
# partition offset_x and offset_y for the outline
cl.shiftPartition( 0.7, 0.7 )
# Fill up the space using vertical line through X
# input : outline list, addition bead spacing
# 6.1 Fill up the base
baseV = cl.FillSpaceX( shapeV, 0 )
# 6.2 Fill up shapeV1  - line fill
arcV1 = cl.FillSpaceX( shapeV1, 1.5 )
# 6.3 Fill up shapeV2 - polygon fill
cl.shiftPartition( 1.7, 2.4 )
arcV2 = cl.FillArbitrary( shapeV2a, ds2, dL2, n2_up, n2_low )
# 6.4 Fill upper half space
cl.shiftPartition( 0.7, 0.7 )
upperV = cl.FillSpaceX( shapeU, 0 )
bottomV = cl.FillSpaceX( shapeD, 0 )


###############################
# Start construct each layer  #
###############################

# Height of the base
nSlice = int(rcp.nLayer)
z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh
zz = z0

# Output the skirt or shape outline
cl.getResult(skirtV, zz, rs, rx, ry, rz, rE, True)
# this is just to make the skirt or outline to other color
#for i in range(len(rs)) :
#    rs[i]  = 2

for i in range( nSlice ) :
    print( ' z = %.3f ' %( zz ))
    cl.getResult(shapeV, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(baseV, zz, rs, rx, ry, rz, rE, True)
    zz = zz + dz


for i in range( int(nGLayer) ) :

    # Polygon Fill
    print( ' z = %.3f ' %( zz ))
    cl.getResult(shapeV1, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(arcV1, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(shapeV2, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(arcV2, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(shapeU, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(upperV, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(shapeD, zz, rs, rx, ry, rz, rE, True)
    cl.getResult(bottomV, zz, rs, rx, ry, rz, rE, True)
    zz = zz + dz

gc = GCodeGenerator( rs, rx, ry, rz, rE, rcp.Fval, rcp.rho )
gc.setMixingRatio( rcp.index )
gc.initTool()
# Setup gliding time and eRatio for incoming and outgoing of an angle
#gc.SetGlideSpeed( 300, 300 )
#gc.Gliding( 0.2, 0.1 , 0.2, 0.2, rs, rx, ry, rz, rE )
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
plt.xlim([5, 355])
plt.ylim([5, 355])
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