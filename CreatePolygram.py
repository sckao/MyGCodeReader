import math
import numpy as np
import matplotlib.pyplot as plt

from GCodeGenerator import GCodeGenerator
from GCodeGenerator import dTheta
from GCodeGenerator import dLength
from Polygram import Polygrams


polyObj = Polygrams()
polyObj.Configure()
rs = []
rx = []
ry = []
rz = []
rE = []


#polyObj.Construct2D(rs, rx, ry)
polyObj.AddSkirt(rs, rx, ry, rz, rE )
polyObj.Construct3D(rs, rx, ry, rz, rE )
#polyObj.SetGlideSpeed(1000,1000)
#polyObj.Gliding( 0.06, 0.1 , 0.06, 0.1, rs, rx, ry, rz, rE)

# Output GCode
gc = GCodeGenerator( rs, rx, ry, rz, rE, polyObj.Fval )
#gc.SetGlideSpeed( polyObj.gFval1, polyObj.gFval2 )
gc.SetGlideSpeed( 2000, 3000 )
gc.Gliding( 0.06, 0.1 , 0.06, 0.1, rs, rx, ry, rz, rE )

gc.Shift( 150, 150, 0 )
gc.Generate()

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Polygram', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([-55, 55])
plt.ylim([-55, 55])
plt.grid(b=True, which='major')
ax.scatter( polyObj.x,  polyObj.y,  s=50, marker= 'o', facecolors='none', edgecolors='red' )
#ax.scatter( polyObj.xt, polyObj.yt, s=50, marker= '^', facecolors='none', edgecolors='blue' )

# Start Routing (x,y) -> (xt,yt) -> (x,y)
print( ' total point %d ' %( len(rx)) )
x_ = rx[0]
y_ = ry[0]
nPoint = len( rx )
n = polyObj.n
for i in range( nPoint -1 ) :
    dX = rx[i+1] - x_
    dY = ry[i+1] - y_
    # print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
    if i == 0 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='green', picker=5)
    #elif (i%(n*2+1) ) == (n*2):
    elif rs[i+1] == 0:
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='red', picker=5)
    elif rs[i+1] == 1 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='purple', picker=5)
    elif rs[i+1] == 3 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='blue', picker=5)
    elif rs[i+1] == 4 :
        ax.quiver(x_, y_, dX, dY, angles='xy', scale_units='xy', scale=1, color='black', picker=5)
    else :
        continue

    x_ = rx[i+1]
    y_ = ry[i+1]

plt.show()




