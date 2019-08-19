import matplotlib.pyplot as plt
import numpy as np
#from mpl_toolkits import mplot3d

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from GWords import GWords



def SetQuiver( ax, gV,  X0 = 0. , Y0 = 0., Z0 = 0. ) :

    # adding vectors
    X = X0
    Y = Y0
    Z = Z0

    j = 0
    for it in gV :
        # XYZ movement
        if  j != len(gV)-1  :

            dX = it[0] - X
            dY = it[1] - Y
            dZ = it[2] - Z
            #print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
            ax.quiver( X, Y, Z, dX, dY, dZ , color= it[4], arrow_length_ratio=0.02  )
            print(' (%.3f, %.3f %.3f => %.3f, %.3f %.3f )' %(X,Y,Z, dX, dY, dZ) )

            X += dX
            Y += dY
            Z += dZ

        j = j+1

def TestSurfacePlot(ax) :

    x = [ 0,1,2,3,3,2,1,0,0,1,2,3,4 ]
    y = [ 1,1,1,1,2,2,2,2,3,3,3,3,2 ]
    z = [ 5,6,6,5,7,8,7,9,8,8,8,8,8 ]

    u = []
    v = []
    w = []
    xa = []
    ya = []
    za = []

    lx = 4


    for i in range( len(x) ) :

        xa.append( x[i] )
        ya.append( y[i] )
        za.append( z[i] )
        if i%4 == 3 :
            print(xa)
            u.append(xa.copy() )
            v.append(ya.copy() )
            w.append(za.copy() )
            xa.clear()
            ya.clear()
            za.clear()


    print('====================')
    print(u)
    print(v)
    print(w)

    ua = np.array(u)
    va = np.array(v)
    wa = np.array(w)

    #surf = ax.plot_surface( ua,va,wa, cmap = cm.coolwarm, linewidth=0 )
    ax.plot_trisurf(x, y, z, linewidth=0.2, antialiased=True)
    ax.set_zlim( 0. , 12.0 )



def SetSurfacePlot( ax, gV) :


    # adding vectors
    xa = []
    ya = []
    za = []

    print(' len = %d ' %(len(gV) ) )
    for i in range( len(gV) ) :
        # XYZ movement

        #if i < 10 :
        #    print(' ( [%d]  %.3f, %.3f %.3f )' %( i, gV[i][0], gV[i][1], gV[i][2] ) )
        if gV[i][2] > 2  :
            continue ;

        xa.append( gV[i][0] )
        ya.append( gV[i][1] )
        za.append( gV[i][2] )



    #surf = ax.plot_surface(xa,ya,za, cmap = cm.coolwarm, linewidth=0 )
    ax.plot_trisurf(xa, ya, za, linewidth=0.2, antialiased=True)
    ax.set_zlim( 0. , 2.5 )


##############################################
#           Main : Start Reading             #
##############################################

# Read files and output GCode results
fname    = input('Read filename : ')
f = open(fname, 'r+')


# position and color list for drawing plots
v = []

i = 0
gd = GWords()

for line in f:
    #print(line, end='')

    if len( line ) < 1 :
        print( ' line size = ' + str( len(line)) )
        continue

    # Read line from the file
    gd.readline( line )
    if gd.posUpdated() :
       print( " A %d - XYZ moved ! " %(i))
    # Get command ( G, M or ... )
    gd.getCommand()
    cmd = gd.command
    # Get X Y Z E F
    gd.getPos()

    if cmd == 'G28':
        print(' Home - Initialized ' + cmd +' \n')
        v.append( [ 0, 0, 0, 0, 'black', 0 ] )

    # if one of x,y,z moved
    if  gd.posUpdated() :
        #print( " B %d - XYZ [%d , %d , %d] ! " %(i, gd.update[0], gd.update[1], gd.update[2]))
        #print( " = XYZ [%.3f , %.3f , %.3f,  %.3f] ! " %( gd.xVal, gd.yVal, gd.zVal, gd.eVal))

        # Record each position and motion type with its color code
        v.append( [gd.xVal, gd.yVal, gd.zVal, gd.eVal, gd.color, gd.moveType ] )

        i = i+1

    if cmd == 'M84':
        print('This layer has %d vector ' %( len(v) ) )


f.close()



fig = plt.figure()
ax = fig.add_subplot( 111, projection='3d' )

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Plot XY limit and grid
plt.xlim([0, 250])
plt.ylim([0, 250])
plt.grid(b=True, which='major')

#SetQuiver( ax, v )
SetSurfacePlot(ax, v)
#TestSurfacePlot(ax )

plt.show()
