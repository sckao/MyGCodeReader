import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class CSVReader :

    def __init__(self):

        csvfilename = input('csv filename : ')
        if csvfilename == '':
            csvfilename = 'test.csv'

        self.file = open(csvfilename, 'r+')
        self.lines = self.file.readlines()

        self.nCol  = input('Number of data column : ')
        if self.nCol == '':
            self.nCol = 3
        else :
            self.nCol = int( self.nCol )

        self.dtype = 'f'

    def setDataType(self):

        dtype_input = input('Data types ( float(f) or string(s) ? separated by "," )' )
        if dtype_input == '':
           dtype_input = 'f'

        self.dtype = dtype_input.split(',')

        if len(self.dtype) == 1 and nCol > 1 :

            n = nCol - len(self.dtype)
            tp0 = self.dtype
            for i in range(n) :
                self.dtype.append(tp0)


    def getData(self):

        i = -1
        vlist = []
        for line in self.lines:

            i = i +1
            if len( line ) < 1 :
                print( ' line size = ' + str( len(line)) )

            if line[0] == '#' :
                continuea

            vals = line.split(',')

            row = []
            for i in range(len(vals)) :

                if self.dtype[i] is 'f' :
                    row.append( float( vals[i] ) )
                else
                    row.append( vals[i] )

            vlist.append(row)

    def closeFile(self):

        self.file.close()

##############################################
#           Main : Start Reading             #
##############################################


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
