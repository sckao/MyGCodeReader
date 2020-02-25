import math
import numpy as np
from ModelMotion import *

# Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
#    y = mx + d
#  |y1| = | x1  1 | | m |
#  |y2|   | x2  1 | | d |
#   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
def SolveLine( x1, y1, x2, y2 ) :
    if x1 == x2 :
        x2 = x2*0.9999999

    a = np.array( [[ x1, 1.] , [ x2, 1.]]  )
    b = np.array( [y1, y2 ]  )
    c = np.linalg.solve(a,b)
    m = c[0]
    d = c[1]

    return m,d

# Solve two line ( y = mx + d )
# return intersection point x,y
def Intersection( m1, d1, m2, d2 ) :
    if m1 == m2 :
        m1 = m1*1.0000001
        m2 = m2*0.9999999

    a = np.array( [[m1, -1.], [m2, -1.]] )
    b = np.array( [ -1*d1, -1*d2 ] )
    c = np.linalg.solve(a, b)
    x = c[0]
    y = c[1]
    return x,y
    # print( '(%d,%d) = [ %.3f, %.3f ]' %( i, j, c[0], c[1]) )

class ConcentricFill:

    def __init__(self):

        print('Class start')



    # updown follow right hand rule
    # updown indicate the outline's direction, clockwise or counter-clockwise, using right-hand rule
    # updown = True means counter-clockwise
    # p2 -> i+1 , p1 -> i
    def findParallel(self, p1, p2, dr, updown = True ):

        #print(' p1=[%.2f, %.2f]  p2=[%.2f, %.2f] ' %(p1[0], p1[1], p2[0], p2[1] ) )
        # exclude same point
        if p1[0] == p2[0] and p1[1] == p2[1] :
            print('Find Parallel Fail !!')
            return []

        ## Solve line - need to consider the solution for vertical & horizontal lines
        # slope for this segment
        m0 = 999999999
        # slope for the orthogonal line
        m  = 999999999
        xc = (p1[0] + p2[0])/2
        yc = (p1[1] + p2[1])/2
        if p2[0] != p1[0] :
            m0 = (p2[1] - p1[1]) / (p2[0] - p1[0])
            if m0 != 0 :
                m = -1/m0
            #else :
            #    return [ 0, yc+dr, xc, yc+dr ]
        else :
            m = 0
            #xs1 = xc + dr
            #ys1 = yc
            #return [ m0, xc*m0 , xs1, ys1]



        # Found the offset centroid point
        # atan return angle between -pi/2 ~ pi/2
        theta = math.atan(m)
        # dx will be always positive
        dx = abs(dr)*math.cos(theta)
        # dy has the same sign as tan
        dy = abs(dr)*math.sin(theta)

        # two possibilities
        xs1 = xc + dx
        ys1 = yc + dy
        if m0 >= 999999998. :
            xs1 = xc + dr
            ys1 = yc
        b1 =  ys1 - (m0*xs1)

        xs2 = xc - dx
        ys2 = yc - dy
        if m0 >= 999999998. :
            xs2 = xc - dr
            ys2 = yc
        b2 =  ys2 - (m0*xs2)

        # Calculate cross-product - use cross-product to determine the point is inside/outside the shape
        # vector 1 from the shape
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        ux1 = xs1 - p1[0]
        uy1 = ys1 - p1[1]
        #ux2 = xs2 - p1[0]
        #uy2 = ys2 - p1[1]
        # vector 2 from the orthogonal vector
        #axb =  (vx*dy - dx*vy )
        axb1 =  (vx*uy1 - ux1*vy )
        #axb2 =  (vx*uy2 - ux2*vy )


        # outline CCW and go outward
        if updown is True and dr > 0 :
            if axb1 < 0 :
                return [m0, b1, xs1, ys1]
            else :
                return [m0, b2, xs2, ys2]

        # outline CCW and go inward
        if updown is True and dr < 0:
            if axb1 > 0 :
                return [m0, b1, xs1, ys1]
            else :
                return [m0, b2, xs2, ys2]

        # outline CW and go outward
        if updown is False and dr > 0 :
            if axb1 > 0 :
                return [m0, b1, xs1, ys1]
            else :
                return [m0, b2, xs2, ys2]

        # outline CW and go inward
        if updown is False and dr < 0:
            if axb1 < 0 :
                return [m0, b1, xs1, ys1]
            else :
                return [m0, b2, xs2, ys2]


    # updown follow right hand rule
    # updown indicate the outline's direction, clockwise or counter-clockwise, using right-hand rule
    # updown = True means counter-clockwise
    def GetOutline(self, shapeV, dr,  updown = True ):

        newOutline = []
        for i in range( len(shapeV) ) :

            if i < len(shapeV)-1 :
                j = i+1
            else :
                j = 0

            if shapeV[i][0] == shapeV[j][0] and shapeV[i][1] == shapeV[j][1] :
                print(' skip duplicated point (%d) to [%d] !! ' %(i, j))
                continue
            if shapeV[i][0] == shapeV[i-1][0] and shapeV[i][1] == shapeV[i-1][1] :
                print(' skip duplicated point (%d) !! ' %(i) )
                continue


            pln1 = self.findParallel( shapeV[i-1], shapeV[i], dr, updown )
            pln2 = self.findParallel(   shapeV[i], shapeV[j], dr, updown )
            #print(' (%d) , sz1= %d , sz2= %d ' %(i, len(pln1), len(pln2) ) )
            if len(pln1) < 1 or len(pln2) < 1 :
                print(' find parallel line fail !! ' )
                continue

            xs, ys = Intersection( pln1[0], pln1[1], pln2[0], pln2[1] )
            #print( '(%d) m1: (%.2f, %.2f) , m2: (%.2f, %.2f) => %.2f, %.2f ' %(i, pln1[0], pln1[1], pln2[0], pln2[1], xs, ys ))
            if pln1[0] == pln2[0] :
                print('->  m = %.2f + %.2f , (%.2f, %.2f) ' %(pln1[0], pln1[1], pln1[2], pln1[3]))
                print('    m = %.2f + %.2f , (%.2f, %.2f) ' %(pln2[0], pln2[1], pln2[2], pln2[3]))
                L12 = length( shapeV[i-1], shapeV[i] )
                L23 = length( shapeV[i], shapeV[j] )
                L13 = L12 + L23
                r12 = L12/L13
                xs = pln1[2] + (pln2[2] - pln1[2])*r12
                ys = pln1[3] + (pln2[3] - pln1[3])*r12


            skip = False
            if len(newOutline) < 1 or skip is True :
                newOutline.append( [xs,ys] )
                skip = False
            else :
                # this part of judgement may not be useful ....
                L12 = length( shapeV[i-1], shapeV[i] )
                L12i = length( newOutline[-1], [xs,ys])
                Lij  = length( [xs,ys] , shapeV[j] )
                if L12i < L12*2 and Lij > abs(dr) :
                    newOutline.append( [xs,ys] )
                else :
                    skip = True
                    print(' skip this point %.2f , %.2f' %(xs,ys) )
                    #newOutline.append( [xs,ys] )

        return newOutline

    def XYRange(self, shapeV ):

        # find maximum dx and dy
        minX = 9999
        maxX = 0
        minY = 9999
        maxY = 0
        for it in shapeV :
            if it[0] < minX :
                minX = it[0]
            if it[0] > maxX :
                maxX = it[0]
            if it[1] < minY :
                minY = it[1]
            if it[1] > maxY :
                maxY = it[1]

        xR = maxX - minX
        yR = maxY - minY

        return xR, yR

    def Fill(self, shapeV, dr, updown = True ):

        xR, yR = self.XYRange(shapeV )
        dX = xR
        dY = yR

        print(' xR :%.2f , yR : %.2f ' %(xR, yR) )
        print( ' pos0 [%.2f, %.2f] , pos-1 [%.2f, %.2f]' %(shapeV[0][0], shapeV[0][1], shapeV[-1][0], shapeV[-1][1] ))


        sV = shapeV.copy()
        fillV = shapeV.copy()
        for i in range (2):
            sTemp = self.GetOutline( sV, dr, updown  )
            sV = sTemp.copy()
            fillV = fillV + sTemp


        '''
        while dX > 0 and  dY > 0 :

            sTemp = self.GetOutline( sV, dr, updown  )
            sV = sTemp.copy()
            fillV = fillV + sTemp
            dX = dX - (2*dr)
            dY = dY - (2*dr)
        '''
        return fillV
