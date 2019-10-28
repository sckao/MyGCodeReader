import matplotlib.pyplot as plt
from GCodeGenerator import GCodeGenerator
from ReadRecipe import ReadRecipe
from PolygonFill import PolygonFill
from Polygram import Polygrams

# Get basic 8 printing parameters
rcp = ReadRecipe('formNext_rcp_10.txt')
rcp.getPrintable()

x= []
y= []

# containers for printing path
rs = []
rx = []
ry = []
rz = []
rE = []


# Setup the outer ring
# Basics for the ring configuration
polyObj = Polygrams()
polyObj.setPrintable( rcp.Fval, rcp.rho, rcp.bh, rcp.ts, rcp.fh, rcp.bs, rcp.nLayer )
#polyObj.setCenter(102.5, 75)
polyObj.setCenter(110, 108)
polyObj.setGeometry(70., 72.5, 36, 0)

# Basics for the Polygon
polychain = PolygonFill()
# Setup                    fval,      rho,  beadwidth
polychain.setParameters( rcp.Fval, rcp.rho, rcp.bs )
# Setup    tip spacing, bead height, first bead height
z0 = polychain.setTipHeight( rcp.ts, rcp.bh, rcp.fh )
spacing_scale = 0.75
polychain.setArcSpacing( spacing_scale)

# Grid printing configuration
iniX = rcp.getParameter('InitX')
iniY = rcp.getParameter('InitY')
n_up = int ( rcp.getParameter('N_up') )
n_low = int ( rcp.getParameter('N_low') )
ds = rcp.getParameter('ds')
dL = rcp.getParameter('dL')
# Thickness of the print
nBead = int( rcp.getParameter('NBead') )
# Height of the print
nSlice = int(rcp.nLayer)
yscale = rcp.getParameter('YScale')
dr = ds + dL
LV = [    dr*3, dr*5,   dr*5,  dr*5,    dr*5,   dr*5,   dr*3 ]
xV0 = [   22.5,    0,      0,     0,       0,      0, 22.5]
w0 , h0 = polychain.unitSize(ds,dL,n_up, n_low, nBead, yscale)
x1 = iniX
y1 = iniY
dd = polychain.beadwidth*spacing_scale*2

yV = []
xV = []
for i in range( len(LV) ):
    x1 = iniX + xV0[i]
    xV.append( x1 )
    yV.append( y1 )
    y1 = y1 - h0 - ((polychain.beadwidth)*2 ) + dd
    #y1 = y1 - h0 - ((polychain.beadwidth)*2 ) + dd - i*0.25*polychain.beadwidth
    #y1 = y1 - h0 - ((polychain.beadwidth)*2 )
    #iniX = iniX  - (polychain.beadwidth/math.tan( math.pi/(n_up+n_low+2) ))

#polychain.addSkirt(iniX, iniY, LV, ds, dL, n_up, n_low, nLayer, 10, scale)
#polychain.getData4Gcode(rx,ry,rz,rs,rE)
#print( ' skirt size = %d' %(len(rx)))

###############################
# Start construct each layer  #
###############################

z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh + rcp.ts
zz = z0
# Add skirt of the circle
polyObj.AddSkirt(rs, rx, ry, rz, rE )

for i in range( nSlice ) :

    if i > 0 :
        polychain.reset()

    polyObj.Construct2D(zz, rs, rx, ry, rz, rE, False )
    x, y = polychain.FillAreaN(xV, yV, LV, ds, dL, n_up, n_low, nBead, zz, yscale)
    polychain.getData4Gcode(rx,ry,rz,rs,rE,True)
    print( ' z = %.3f ' %( zz ))
    zz = zz + dz

gc = GCodeGenerator( rs, rx, ry, rz, rE, rcp.Fval, rcp.rho )
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