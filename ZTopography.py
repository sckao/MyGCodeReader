from scipy import optimize
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import math


class ZTopography:

    def __init__(self):
        self.nX = 10
        self.nY = 10
        self.fitPara = ()
        self.nOrder = 2


    def readData(self, fname = 'heightmap.csv' ) :

        f = open(fname, 'r+')

        axisName = []
        axisInfo = []
        getNextLine = False
        getValue = False
        zValsAll = []
        for ln in f:

            line = ln.split(',')
            print('line size = %d' %(len(line)) )
            if len(line) < 2:
                continue ;
            if line[0] == 'xmin' :
                getNextLine = True
                for i in range(len(line)) :
                    axisName.append( line[i] )
            elif getNextLine is True :
                for i in range(len(line)) :
                    axisInfo.append( float(line[i]) )
                getNextLine = False
                getValue = True

            elif getValue == True :
                vals = ln.split(',')
                fVals = []
                for it in vals :
                    fVals.append( float(it) )

                zValsAll.append(fVals)

        self.nX = int(axisInfo[7])
        self.nY = int(axisInfo[8])
        # Get X grid
        x = axisInfo[0]
        xV = []
        for i in range( self.nX - 1  ) :
            xV.append( x )
            x = x + axisInfo[5]
        xV.append( axisInfo[1] )

        xM = np.array( xV )
        xMap = np.tile(xM, ( self.nY,1)  )

        print( 'xV' )
        print( xV )
        print( 'xM' )
        print( xMap )

        y = axisInfo[2]
        yV = []
        for i in range( self.nY - 1  ) :
            yV.append( y )
            y = y + axisInfo[6]
        yV.append( axisInfo[3] )

        yM = np.array( yV )
        yMap = np.tile(yM, ( self.nX,1)  ).transpose()

        print( 'yV' )
        print( yV )
        print( 'yM' )
        print( yMap )


        zMap = np.array( zValsAll )
        print( 'zM' )
        print( zMap )

        return zMap, xMap, yMap

    # read data from a csv file with format X,Y,Z
    def readXYZfile(self, fName = 'zmap.csv' ):

        f = open( fName, 'r+')

        xV = []
        yV = []
        zV = []
        for ln in f:

            words = ln.split(',')
            if len(words) < 3:
                continue ;

            else :

                if words[0][0:1] == '#' or words[0][0:1] == ';':
                    continue ;

                else :
                    xV.append( float(words[0]) )
                    yV.append( float(words[1]) )
                    zV.append( float(words[2]) )

        xA = np.array( xV )
        yA = np.array( yV )
        zA = np.array( zV )

        return zA, xA, yA


    def find_init_parameters(self, data, x, y ):

        print('data - sz' )
        print( data.shape)

        dzdx = 0.
        dzdy = 0.
        zAve = np.average(data)
        sz = len( data.shape )
        if sz == 2 :
            nx = data.shape[1]
            ny = data.shape[0]
            ave_Zx = np.average(data[0:1,0:nx ])
            ave_Zy = np.average(data[0:ny,0:1 ])
            print("ave Zx = %.5f , Zy = %.5f" %( ave_Zx, ave_Zy) )
            dx = x[0,0] - x[0,nx-1]
            dy = y[0,0] - y[ny-1,0]
            dzdx = ave_Zy / dx
            dzdy = ave_Zx / dy
            print(" dy = %.3f  dx = %.3f" %(dy, dx) )
            print(" aveZ= %.5f dZ/dy = %.6f  dZ/dx = %.6f" %(zAve, dzdy, dzdx) )
        if sz == 1 :
            min_xi = np.argmin(x)
            min_x = x[ min_xi]
            max_xi = np.argmax(x)
            max_x = x[ max_xi]
            print('min x [%d] : %.3f ' %(min_xi, min_x) )
            print('max x [%d] : %.3f ' %(max_xi, max_x) )
            min_yi = np.argmin(y)
            min_y = x[ min_yi]
            max_yi = np.argmax(y)
            max_y = x[ max_yi]
            print('min y [%d] : %.3f ' %(min_yi, min_y) )
            print('max y [%d] : %.3f ' %(max_yi, max_y) )



    def plane_surface(self, x, y, p , nO = 2 ):

        if nO == 1 or len(p) < 4 :
            z = p[0] + (p[1]*x) + (p[2]*y)
        elif nO ==2 or len(p) < 7 :
            z = p[0] + (p[1]*x) + (p[2]*y)+ (p[3]*x*x) + (p[4]*y*y) + (p[5]*x*y)
        elif nO ==3  or len(p) < 11 :
            z = p[0] + (p[1]*x) + (p[2]*y)+ (p[3]*x*x) + (p[4]*y*y) + (p[5]*x*y) + (p[6]*x*x*y) + (p[7]*x*y*y) + (p[8]*x*x*x) + (p[9]*y*y*y)
        else :
            z = p[0] + (p[1]*x) + (p[2]*y)+ (p[3]*x*x) + (p[4]*y*y) + (p[5]*x*y)

        return z

    def fitSurface(self, data, xSpc, ySpc, nOrder = 2 ):

        print( " Data Shape " )
        print( data.shape )
        self.nOrder = nOrder

        p =  ( 2 ,   0.01, 0.02,  0.0, 0.0, 0.0 )
        p0 = ( 2 , 0.012, 0.022, 0.0, 0.0, 0.0 )
        if nOrder == 1:
            p =  ( 0.1 , 0.001, -0.02 )
            p0 = ( 0.1 , 0.001, -0.02 )
        if nOrder == 3:
            p =  ( 0.1 , 0.001, -0.001,  0.0, 0.0, 0.0, 0., 0., 0., 0. )
            p0 = ( 0.1 , 0.001, -0.001, 0.0, 0.0, 0.0 , 0., 0., 0., 0. )

        errF = lambda p,x,y,z : np.ravel( self.plane_surface( x, y, p, nOrder) - z )
        p1, cov = optimize.leastsq( errF, p0, ( xSpc, ySpc, data )  )
        print( " Fitted Shape " )
        print( p1.shape )
        #print(" 2D fitted p1 = %.5f, %.5f, %.5f, %.5f, %.5f  %.5f, %.5f, %.5f, %.5f  %.5f"
        #      %(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5], p1[6], p1[7], p1[8], p1[9]) )
        #print(" 2D fitted p1 = %.5f, %.5f, %.5f, %.5f, %.5f  %.5f" %(p1[0], p1[1], p1[2], p1[3], p1[4], p1[5]) )
        #print(" 2D fitted p1 = %.5f, %.5f, %.5f " %(p1[0], p1[1], p1[2] ) )
        print(" 2D fitted parameters :")
        self.fitPara = p1
        print( self.fitPara )

        fitData = self.plane_surface( xSpc, ySpc, p1, nOrder )
        print( " fit Data Shape " )
        print( fitData.shape )

        return fitData



#################
#  Test ground  #
#################

'''

ff2d = fitting2D()

z,x,y = ff2d.readData()
#z,x,y = ff2d.readXYZfile()

ff2d.find_init_parameters(z,x,y)

#z,x,y = ff2d.fake_surface_data()

fitData = ff2d.fitSurface(z,x,y,3)

fig = plt.figure( figsize=(7.5,7.5) )
ax = fig.gca( projection= '3d' )
ax.scatter( x,y,z, c='r', marker='o' )
ax.plot_surface( x,y,fitData, rstride=1, cstride=1, cmap='viridis', edgecolor='none' )
#ax.plot_trisurf( x,y,fitData  )

plt.show()
'''
