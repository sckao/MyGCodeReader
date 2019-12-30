import matplotlib.pyplot as plt
import math
from GWords import GWords
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from AreaFill import AreaFill
#from Polygram import Polygrams
from Ellipse import Ellipse

# Rotate (x,y) CounterClockwise
#  |x|    [ cos   -sin ] | x0 |
#  |y| =  [ sin    cos ] | y0 |
def rotation( pos, theta ) :

    x0 = pos[0]
    y0 = pos[1]
    x = x0*math.cos(theta) - y0*math.sin(theta)
    y = x0*math.sin(theta) + y0*math.cos(theta)
    pos[0] = x
    pos[1] = y

    return x,y

def zoom( pos, scale ) :

    x0 = pos[0]
    y0 = pos[1]
    r0 = math.sqrt( (x0*x0) + (y0*y0) )
    cos = x0/r0
    sin = y0/r0

    r = r0*scale
    x = r*cos
    y = r*sin
    pos[0] = x
    pos[1] = y

def shift( pos, dx, dy ) :

     pos[0] = pos[0] + dx
     pos[1] = pos[1] + dy



   # Read outline from a gcode
def ReadOutline( ) :
    # Read GCode File
    fname = input('Read filename : ')
    f = open(fname, 'r+')

    gd = GWords()
    v = []
    i = 0
    for line in f:

        if len(line) < 1:
            continue

        # 1. Read line from the file
        gd.readline(line)

        # 2. Get command ( G, M or ... )
        gd.getCommand()
        cmd = gd.command

        # 3. Get X Y Z E F
        gd.getPos()

        if gd.posUpdated():

            xi = gd.xVal
            yi = gd.yVal
            if gd.xVal ==0  and gd.yVal == 0 :
                continue

            pos = [xi,yi]
            rotation( pos, -0.5*math.pi )
            shift( pos, -150, 350 )
            zoom(  pos, 0.7)

            xj = pos[0]
            yj = pos[1]


            print(' shape [%d] (%.2f, %.2f)' %(i, xj, yj) )
            v.append([xj, yj])
            i = i+1


    v.append( [v[0][0], v[0][1]] )
    if len(v) > 0 :
        vx0 = v[0][0]
        vy0 = v[0][1]
        vx1 = v[-1][0]
        vy1 = v[-1][1]

        if vx0 == vx1 and vy0 == vy1 :
            print(' Closed Loop !' )
        else :
            print(' NOT Closed Loop !' )

    return v

###################################################
#             Springer project code               #
###################################################

# Get basic 8 printing parameters
rcp = ReadRecipe('springer_rcp.txt')
rcp.getPrintable()

x= []
y= []

# containers for printing path
rs = []
rx = []
ry = []
rz = []
rE = []

# 1. Makeup a shape for test

#                   a   b   x0 y0
#ellipse = Ellipse( 25, 50, 80, 80 )
#shapeV = ellipse.getEllipse()

#ellipse = Ellipse( 27, 54, 80, 80 )
#skirtV = ellipse.getEllipse()

# Read a GCode Shape file
shapeV = ReadOutline()

# Generate outer wall and skirt
skirtV = []
xc = 0
yc = 0
xc1 = 0
yc1 = 0
for it in shapeV :

    skirtP = [ it[0], it[1] ]
    zoom(  skirtP, 1.1)
    skirtV.append( skirtP )

    xc  = xc + it[0]
    yc  = yc + it[1]
    xc1 = xc1 + skirtP[0]
    yc1 = yc1 + skirtP[1]

xc  = xc/len(shapeV)
yc  = yc/len(shapeV)
xc1 = xc1/len(shapeV)
yc1 = yc1/len(shapeV)
d_x = xc - xc1
d_y = yc - yc1

for it in skirtV :
    shift( it, d_x, d_y )



# Divide the shoe shape into 3 parts
shapeV1 = []
shapeV2 = []
shapeV3 = []

# partition shape into upper and lower parts
for it in shapeV :

     if it[1] > 150 :
         shapeV1.append( [ it[0], it[1] ] )

     if it[1] < 150 and it[1] > 100 :
         shapeV2.append( [ it[0], it[1] ] )

     if it[1] < 100 :
         shapeV3.append( [ it[0], it[1] ] )


# 2. Basics for the Grids

# Grid printing configuration
dL = rcp.getParameter('dL')
ds = rcp.getParameter('ds')

#yspacing_scale = 0.5
#polychain.setArcSpacing( yspacing_scale)

# Number of turn at upper and lower polygon
n_up = int ( rcp.getParameter('N_up') )
n_low = int ( rcp.getParameter('N_low') )
# Height of the print
nSlice = int(rcp.nLayer)


# to set up initial y position
delta = ds*1.1

# Start constructing
cl = AreaFill()
cl.setPrintable(rcp.Fval, rcp.rho, rcp.bs )
print(' Find Middle XBoundary !!')
xL1, xR1 = cl.findXBoundary(150, shapeV)
xL2, xR2 = cl.findXBoundary(100, shapeV)

shapeV2.insert( 0, [xL1[0], 150] )
shapeV2.append( [xR1[0], 150] )
for i in range( len(shapeV2 )) :
    if shapeV2[i][0] <  60 and shapeV2[i+1][0]> 60 :
        shapeV2.insert(i+1, [xL2[0], 100] )
        shapeV2.insert(i+2, [xR2[0], 100] )
        break


shapeV3.insert( 0, [xL2[0], 100] )
shapeV3.append( [xR2[0], 100] )

# Start Filling
#arcV = cl.FillArbitrary( shapeV, ds, dL, n_up, n_low )
print(' Get upper part ')
arcV1 = cl.FillArbitrary( shapeV1, ds, dL, n_up, n_low )
print(' Get lower part ')
arcV2 = cl.FillArbitrary( shapeV2, 70, 2, 0, 0 )
print(' dL = %.3f , ds = %.3f ' %(dL, ds))
arcV3 = cl.FillArbitrary( shapeV3, 10, 0, 1, 1 )
print(' dL = %.3f , ds = %.3f ' %(dL, ds))

arcV = []
for it in arcV1 :
    arcV.append( [ it[0], it[1]] )
for it in arcV2 :
    arcV.append( [ it[0], it[1]] )
for it in arcV3 :
    arcV.append( [ it[0], it[1]] )


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

# Output the skirt or shape outline
#cl.getResult(skirtV, zz, rs, rx, ry, rz, rE, True)
#cl.getResult(shapeV, zz, rs, rx, ry, rz, rE, True)

for i in range(len(rs)) :
    rs[i]  = 2

for i in range( nSlice ) :

    # Polygon Fill
    cl.getResult(arcV, zz, rs, rx, ry, rz, rE, True)
    print( ' z = %.3f ' %( zz ))

    #if nSlice == 3 :
    #    dz = dz + 0.1
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
plt.xlim([5, 225])
plt.ylim([5, 225])
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