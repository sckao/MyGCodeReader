import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

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
        #if gV[i][2] > 2  :
        #    continue ;

        xa.append( gV[i][0] )
        ya.append( gV[i][1] )
        za.append( gV[i][2] )



    #surf = ax.plot_surface(xa,ya,za, cmap = cm.coolwarm, linewidth=0 )
    ax.plot_trisurf(xa, ya, za, linewidth=0.2, antialiased=True)
    ax.set_zlim( 290. , 310 )

def GetProfile( gV, nSample = 1280, idx=0 ) :

    xa = []
    ya = []
    za = []
    k  = idx*nSample
    for i in range( nSample ) :

        xa.append( gV[k][0] )
        ya.append( gV[k][1] )
        za.append( gV[k][2] )
        k = k + 1

    para = np.polyfit(xa, ya, 1)
    print( para )

    ave_z = np.average( za )
    std_z = np.std( za )
    stat = [ave_z, std_z]
    return stat

##############################################
#           Main : Start Reading             #
##############################################

# Read files and output GCode results
fname    = input('Read filename : ')
f = open(fname, 'r+')

v = []
# position and color list for drawing plots
i = 0
for line in f:
    #print(line, end='')

    if len( line ) < 1 :
        print( ' line size = ' + str( len(line)) )
        continue

    i = i+1
    if i%10 != 0 :
        continue

    # Read line from the file
    words = line.split()
    x = float( words[0] )
    y = float( words[1] )
    z = float( words[2] )

    v.append([x,y,z])
    #print(' ( %.3f, %.3f, %.3f ) ' %(x,y,z) )

f.close()

#####################################
#       Setup canvas and draw       #
#####################################

fig = plt.figure()
ax = fig.add_subplot( 111, projection='3d' )

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')

# Plot XY limit and grid
plt.xlim([-50, 50])
plt.ylim([0, 250])
plt.grid(b=True, which='major')

# check pedestal
stat = GetProfile(v,1280,0)
print('z0 = %.3f +/- %.3f ' %(stat[0], stat[1]) )
#id = (len(v) /1280) - 1
#print( 'id = %d' %(id))
stat = GetProfile(v,1280,22)
print('z0 = %.3f +/- %.3f ' %(stat[0], stat[1]) )

SetSurfacePlot(ax, v)

plt.show()
