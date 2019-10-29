import matplotlib.pyplot as plt
import math
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
polychain = PolygonFill()
# Setup                    fval,      rho,  beadwidth
polychain.setParameters( rcp.Fval, rcp.rho, rcp.bs )
# Setup    tip spacing, bead height, first bead height
z0 = polychain.setTipHeight( rcp.ts, rcp.bh, rcp.fh )
polychain.setRetraction(5, -1)
yspacing_scale = 0.5
polychain.setArcSpacing( yspacing_scale)

# Grid printing configuration
dL = rcp.getParameter('dL')
ds = rcp.getParameter('ds')
dr = ds + dL
rc = ri - (rcp.bs/2)

print(' dL = %.3f , ds = %.3f ' %(dL, ds))

# Number of turn at upper and lower polygon
n_up = int ( rcp.getParameter('N_up') )
n_low = int ( rcp.getParameter('N_low') )
# Thickness of the print
nBead = int( rcp.getParameter('NBead') )
# Height of the print
nSlice = int(rcp.nLayer)
yscale = rcp.getParameter('YScale')

# Unit size
dd = polychain.beadwidth*yspacing_scale*2
w0 , h0 = polychain.unitSize(ds,dL,n_up, n_low, nBead, yscale)
print(' unit size W:%.3f , h : %.3f ' %(w0, h0))
# Check starting point
w1 = w0 + (dL/2)
x1 = xc - w1
yr = math.sqrt( (rc*rc) - (w1*w1) )
y1 = yc + yr - (rcp.bs*2.75)
NRow = int( yr / (h0+rcp.bs) )*2
print(' Need %d rows ' %(NRow) )

rr = math.sqrt( pow((x1 -xc),2) + pow((y1-yc),2) )
sAng = math.acos( (x1-xc)/rr)
print('start angle is %.3f' %(sAng) )

NEle = 2
m0 = NEle /2
LV = []
xV = []
yV = []
fV = []
for i in range( NRow ):

    # starting point
    xV.append( x1 )
    yV.append( y1 )
    LV.append(dr*NEle)
    print('[%d] (%.2f,%.2f) with %d' %(i, x1, y1, NEle))

    # connecting x y positions
    cArc = []
    y_a = y1 + ( yspacing_scale -1)*rcp.bs
    yr = y_a - yc
    x_a = xc - math.sqrt( (rc*rc) - (yr*yr) )
    cArc.append( [x_a, y_a] )

    # shift y downward
    y1 = y1 - h0 - ((polychain.beadwidth)*2 ) + dd
    yr = y1 - yc
    if abs(yr) > rc :
        fArc = polyObj.GetPolygonB(50,cArc[-1], fV[0][0] , xc, yc )
        for it in fArc :
            cArc.append( it )
        fV.append( cArc )
        print('Stop 1')
        break
    xr = math.sqrt( (rc*rc) - (yr*yr) )
    m = int( (xr -(dL/2))/dr )
    x1 = x1 - (m-m0)*dr
    NEle = 2*m
    m0 = m

    # 2nd connecting point
    if i == NRow -1 :
        fArc = polyObj.GetPolygonB(50,cArc[-1], fV[0][0] , xc, yc )
        for it in fArc :
            cArc.append( it )
        fV.append( cArc )
        print('Stop 2')
    else :
        yr = y1 - yc
        x_b = xc - math.sqrt( (rc*rc) - (yr*yr) )
        cArc.append( [x_b, y1] )
        fV.append( cArc )


###############################
# Start construct each layer  #
###############################

z0 = rcp.bh + rcp.ts + rcp.fh
dz = rcp.bh
zz = z0
# Add skirt of the circle
polyObj.AddSkirt(rs, rx, ry, rz, rE )

for i in range( nSlice ) :

    if i > 0 :
        polychain.reset()

    # Circle
    polyObj.Construct2D(zz, rs, rx, ry, rz, rE, True )
    # Polygon Fill
    #x, y = polychain.FillAreaN(xV, yV, LV, ds, dL, n_up, n_low, nBead, zz, yscale)
    x, y = polychain.FillArea(xV, yV, LV, fV, ds, dL, n_up, n_low, nBead, zz, yscale)
    polychain.getData4Gcode(rx,ry,rz,rs,rE,True)
    print( ' z = %.3f ' %( zz ))
    zz = zz + dz

gc = GCodeGenerator( rs, rx, ry, rz, rE, rcp.Fval, rcp.rho )
gc.SetGlideSpeed( 400, 400 )
# Setup gliding time and eRatio for incoming and outgoing of an angle
gc.Gliding( 0.3, 0.05 , 0.3, 0.05, rs, rx, ry, rz, rE )
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