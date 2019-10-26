import matplotlib.pyplot as plt
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from PolygonFill import PolygonFill
from Polygram import Polygrams

# Get basic 8 printing parameters
rcp = ReadRecipe()
rcp.getPrintable()

x= []
y= []

rs = []
rx = []
ry = []
rz = []
rE = []


# Setup the outer ring
polyObj = Polygrams()
polyObj.setGeometry(70., 72.5,360,0)
polyObj.setPrintable( rcp.Fval, rcp.rho, rcp.bh, rcp.ts, rcp.fh, rcp.bs, rcp.nLayer )
polyObj.AddSkirt(rs, rx, ry, rz, rE )
polyObj.Construct3D(rs, rx, ry, rz, rE )
# Output GCode
gc = GCodeGenerator( rs, rx, ry, rz, rE, polyObj.Fval )
#gc.SetGlideSpeed( polyObj.gFval1, polyObj.gFval2 )

gc.Shift( 102.5, 75, 0 )
gc.Generate()


polychain = PolygonFill()
# Setup                    fval,      rho,  beadwidth
polychain.setParameters( rcp.Fval, rcp.rho, rcp.bs )
# Setup    tip spacing, bead height, first bead height
z0 = polychain.setTipHeight( rcp.ts, rcp.bh, rcp.fh )

spacing_scale = 0.75
polychain.setArcSpacing( spacing_scale)

iniX = 50
iniY = 100
n_up = 2
n_low = 2
ds = 13.125
dL = 6.5625
# Thickness of the print
nLayer = 1
# Height of the print
nSlice = int(rcp.nLayer)
#scale = 0.57735
scale = 1

dr = ds + dL

LV = [    dr*3,    dr*3,  dr*5,    dr*3,    dr*3 ]
xV0 = [19.6875, 19.6875,     0, 19.6875,  19.6875]
yV = []
xV = []
w0 , h0 = polychain.unitSize(ds,dL,n_up, n_low, nLayer, scale)
x1 = iniX
y1 = iniY
dd = polychain.beadwidth*spacing_scale*2
for i in range( len(LV) ):
    x1 = iniX + xV0[i]
    xV.append( x1 )
    yV.append( y1 )
    #y1 = y1 - h0 - ((polychain.beadwidth)*2 ) + dd - i*0.25*polychain.beadwidth
    y1 = y1 - h0 - ((polychain.beadwidth)*2 ) + dd
    #y1 = y1 - h0 - ((polychain.beadwidth)*2 )
    #iniX = iniX  - (polychain.beadwidth/math.tan( math.pi/(n_up+n_low+2) ))

#polychain.addSkirt(iniX, iniY, LV, ds, dL, n_up, n_low, nLayer, 10, scale)
#polychain.getData4Gcode(rx,ry,rz,rs,rE)
#print( ' skirt size = %d' %(len(rx)))

fs = polychain.bh + polychain.ts
zz = z0

for i in range( nSlice ) :

    if i > 0 :
        polychain.reset()

    x, y = polychain.FillAreaN(xV, yV, LV, ds, dL, n_up, n_low, nLayer, zz, scale)
    polychain.getData4Gcode(rx,ry,rz,rs,rE,True)
    print( ' z = %.3f ' %( zz ))
    zz = zz + fs

gc = GCodeGenerator( rs, rx, ry, rz, rE, polychain.Fval, polychain.rho )
gc.Generate()


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