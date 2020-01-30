import matplotlib.pyplot as plt
import math
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from AreaFill import AreaFill
from Quadrilateral import Rectangle
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
# Read a GCode Shape file - 4 different outline shapes
shapeV = ReadOutline( 'InsertOutline.gcode', -60, 300, -0.5*math.pi )
#shapeV1 = ReadOutline( 'InsertOutline1.gcode', -50, 200, -0.5*math.pi )
shapeV2 = ReadOutline( 'InsertOutline2.gcode', -60, 300, -0.5*math.pi )
shapeV1_0 = ReadOutline( 'InsertOutline1c.gcode', -60, 408, -0.5*math.pi )
shapeV1 = rotateList( shapeV1_0, 25 )


# 2. Get skirt of the print and outline of pattern2
cf = ConcentricFill()
skirtV = cf.GetOutline(shapeV, 5, True )
shapeV2a = cf.GetOutline(shapeV2, -1., False )
shapeV1s = cf.GetOutline(shapeV1, 1., False )

# create a smoothing block for the start of infill
recObj  = Rectangle( 20, 5 , 1, 0 )
recObj.Setup( 6, 20, 0, 1, 20, 182)
blockU = recObj.GetShape()
recObj.Setup( 5, 20, 0, 1, 20, 158)
blockD = recObj.GetShape()

# 3. Setup Filling parameters
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
cl.setBeadSpacing( rcp.bs, BSScale)
cl.setTipHeight( rcp.ts, rcp.bh, rcp.fh, rcp.rh )

# 4. Grid printing configuration
nGLayer = rcp.getParameter('GNLayer')
dL2 = rcp.getParameter('dL2')
ds2 = rcp.getParameter('ds2')
n2_up = int ( rcp.getParameter('N2_up') )
n2_low = int ( rcp.getParameter('N2_low') )


# 5. construct the fill around shape1 and shape2
# 5.1 Find the center Y
tB,bB,lB,rB = cl.defineRange( shapeV )
Yc = (tB[1] + bB[1])/2 + 3
Yd = Yc - (rcp.bs*BSScale)
# 5.2 Divide shapeV , shapeV1 and shapeV2 to two halves ( U and D )
shapeU0, shapeD0 = SplitOutline( shapeV, Yc)
shapeU1, shapeD1 = SplitOutline( shapeV1s, Yc)
shapeU2, shapeD2 = SplitOutline( shapeV2, Yc)
# U0, U2 and D2 are closed loop, removed the end
del shapeU0[-1]
del shapeU2[-1]
del shapeD2[-1]

# 5.3 Combine half shapeV + shapeV1 and shapeV2 in the order
shapeU = shapeU0 + [ [33, Yc], [38.5, Yc] ]+ shapeU2 +  [ [122.2, Yc] , [180.5, Yc] ] +  shapeU1 + [[244, Yc], [281.95,Yc]]
#shapeU.append( shapeU[0] )

print(' D0  [%.2f ,%.2f] to [%.2f, %.2f] ' %( shapeD0[0][0], shapeD0[0][1],  shapeD0[-1][0], shapeD0[-1][1] ))
print(' D1  [%.2f ,%.2f] to [%.2f, %.2f] ' %( shapeD1[0][0], shapeD1[0][1],  shapeD1[-1][0], shapeD1[-1][1] ))
print(' D2  [%.2f ,%.2f] to [%.2f, %.2f] ' %( shapeD2[0][0], shapeD2[0][1],  shapeD2[-1][0], shapeD2[-1][1] ))
#del shapeD1[0]
shapeD_a = shapeD0 + [ [281.95, Yd],[244, Yd] ] + shapeD1 + [ [180.5, Yd], [122.5, Yd] ] + shapeD2 + [[38.5, Yd],[34,Yd]]
shapeD_a.append( shapeD_a[0] )
shapeD = rotateList( shapeD_a, 115 )


# 6. Start Filling
# Fill up the space using vertical line through X
# input : outline list, addition bead spacing
# 6.1 Fill up the base
# Fill up outline shapeV with each x step = beadwidth*BSScale + additional delta x (default = 0)
baseV = cl.FillSpaceX( shapeV, 0 )

# 6.2 Fill up shapeV1  - line fill , additional delta x = 1.5 mm
arcV1 = cl.FillSpaceX( shapeV1, 1.5 )

# 6.2a Concentric Fill for shapeV1
#shapeV1a = cf.GetOutline(shapeV1, -4., False )
#Reduce( shapeV1a )
#shapeV1b = cf.GetOutline(shapeV1a, -4., False )
#Reduce( shapeV1b )
#shapeV1c = cf.GetOutline(shapeV1b, -4., False )
#Reduce( shapeV1c )

# 6.3 Fill up shapeV2 - polygon fill
# partition offset_x and offset_y for the outline
cl.shiftPartition( 1.7, 1.9 )
arcV2 = cl.FillArbitrary( shapeV2a, ds2, dL2, n2_up, n2_low )
# 6.4 Fill upper half space
cl.shiftPartition( 0.7, 0.7 )
upperV = cl.FillSpaceX( shapeU, 0, -0.2 )
bottomV = cl.FillSpaceX( shapeD, 0, -0.2 )

# This is connecting path, avoiding drooling
move1 = [ [30,220], [20,220] ]
move2 = [ [65,130], [185,130] ]
move3 = [ [285,184], [285,130], [21,130] ]
move4 = [ [285,185], [285,130], [21,130] ]
# This is smoothing block for starting
uBlock = cl.FillSpaceX( blockU, 0, -0.2 )
dBlock = cl.FillSpaceX( blockD, 0, -0.2 )

###############################
# Start construct each layer  #
###############################

# Height of the base
nSlice = int(rcp.nLayer)
z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh
zz = z0

# Output the skirt or shape outline
cl.getGcode(skirtV, zz, rs, rx, ry, rz, rE)
# this is just to make the skirt or outline to other color
#for i in range(len(rs)) :
#    rs[i]  = 2

for i in range( nSlice ) :
    print( ' z = %.3f ' %( zz ))
    # z = 0.8
    cl.getGcode(shapeV, zz, rs, rx, ry, rz, rE)
    cl.getGcode(move1, zz, rs, rx, ry, rz, rE, 5 )
    zz = zz + 0.3
    # z = 1.1
    cl.getGcode(dBlock, zz, rs, rx, ry, rz, rE)
    cl.getGcode(uBlock, zz, rs, rx, ry, rz, rE)
    cl.getGcode(baseV, zz, rs, rx, ry, rz, rE)
    # Need Tip wipes
    cl.doPurge(5., rs, rx, ry, rz, rE)
    zz = zz + dz


for i in range( int(nGLayer) ) :

    # Polygon Fill
    print( ' z = %.3f ' %( zz ))
    # z = 1.6
    #cl.getGcode(shapeV2, zz, rs, rx, ry, rz, rE)
    cl.getGcode(arcV2, zz, rs, rx, ry, rz, rE)
    cl.doRetract( arcV2[-1], zz, shapeV1[0], zz, move2,  rs, rx, ry, rz, rE,)
    #cl.getGcode(move2, zz, rs, rx, ry, rz, rE, 5 )

    cl.getGcode(shapeV1, zz, rs, rx, ry, rz, rE)
    cl.getGcode(arcV1, zz, rs, rx, ry, rz, rE)
    #cl.getGcode(shapeV1a, zz, rs, rx, ry, rz, rE)
    #cl.getGcode(shapeV1b, zz, rs, rx, ry, rz, rE)
    #cl.getGcode(shapeV1c, zz, rs, rx, ry, rz, rE)

    cl.getGcode(shapeU, zz, rs, rx, ry, rz, rE)
    cl.getGcode(shapeD, zz, rs, rx, ry, rz, rE)
    cl.doRetract( shapeD[-1], zz, uBlock[0], zz+0.35, move3,  rs, rx, ry, rz, rE,)
    #cl.getGcode(move3, zz, rs, rx, ry, rz, rE, 5 )

    zz = zz + 0.35
    # z = 1.95
    cl.getGcode(uBlock, zz, rs, rx, ry, rz, rE )
    cl.getGcode(upperV, zz, rs, rx, ry, rz, rE )
    cl.doRetract( upperV[-1], zz, [281.75, 10], zz, [],  rs, rx, ry, rz, rE,)
    cl.doPurge(5., rs, rx, ry, rz, rE)
    #cl.getGcode(move4, zz, rs, rx, ry, rz, rE, 5 )
    cl.getGcode(dBlock, zz, rs, rx, ry, rz, rE )
    cl.getGcode(bottomV, zz, rs, rx, ry, rz, rE )
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