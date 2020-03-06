import math
import numpy as np
from ModelMotion import rotation
from ConcentricFill import ConcentricFill

# http://www.dcs.gla.ac.uk/~pat/52233/slides/Geometry1x1.pdf

class PatternFill :

    def __init__(self):

        self.bw = 1.75
        self.bsScale = 0.5
        self.bs = self.bw*self.bsScale
        self.yScale = 1.

    def setBeadSpacing(self, bw, bsscale ):

        self.bw = bw
        self.bsScale = bsscale
        self.bs = self.bw*self.bsScale

    # providing shapes from left to right
    # n: number of point in upper/bottom half, radius, dL : spacing
    # flip : upper or bottom half of the polygon
    # phi is rotation angle in CCW
    # return points
    def unitPolygon(self, n, r, dL, x0, y0, flip = False, phi = 0 ) :

        pattern = []
        dA = math.pi / (n+1)

        theta = math.pi
        x = x0
        y = y0
        for i in range(n+2) :
            dx0 = r*math.cos( theta )
            dy0 = r*math.sin( theta )
            if flip is True :
                dy0 = -1*dy0

            dx, dy = rotation( [dx0, dy0] , phi)

            x = x0 + dx
            y = y0 + dy
            pattern.append( [x,y] )
            theta = theta - dA

        tx, ty = rotation( [r+dL, 0], phi)
        #pattern.append( [x+dL, y0] )
        pattern.append( [x0+tx, y0+ty ] )
        return pattern

    # dL is the tail length ( the length to next square )
    # ds is the deviation for 45 degree turn
    # phi is the rotation angle
    def unitSquare(self, h, w, dL, x0, y0, ds = 0, phi = 0 ):

        dsy = ds
        if h < 0 :
            dsy = -1*ds

        pattern = []

        pattern.append( [x0 -ds , y0] )
        if ds != 0 :
            pattern.append( [x0 , y0 + dsy ] )

        pattern.append( [x0, y0+h - dsy] )
        if ds != 0 :
            pattern.append( [x0+ds, y0+h] )

        pattern.append( [x0+w -ds, y0+h] )
        if ds != 0 :
            pattern.append( [x0+w, y0+h-dsy ] )

        pattern.append( [x0+w, y0+dsy] )
        if ds != 0 :
            pattern.append( [x0+w+ds, y0] )

        pattern.append( [x0+w+dL-ds, y0] )

        patternR = []
        for it in pattern :
            xr, yr = rotation( it, phi, x0, y0 )
            patternR.append( [xr, yr] )

        return patternR

    def findRange(self, pos ):

        top  = [ pos[0][0], pos[0][1] ]
        bott = [ pos[0][0], pos[0][1] ]
        left = [ pos[0][0], pos[0][1] ]
        right= [ pos[0][0], pos[0][1] ]

        for it in pos :

            if it[1] > top[1] :
                top = [ it[0], it[1] ]
            if it[1] < bott[1] :
                bott = [ it[0], it[1] ]
            if it[0] > right[0] :
                right = [ it[0], it[1] ]
            if it[0] < left[0] :
                left = [ it[0], it[1] ]

        return top,bott,left,right

    def unitSize(self, pos ):

        top, bott, left, right = self.findRange(pos)

        width = right[0] - left[0]
        height = top[1] - bott[1]

        return width, height

    # This polygon does not take into account of bead spacing between top half and bottom half
    def unitPolygonSize(self, n,m,r,dL ):

        u1 = self.unitPolygon( n, r, dL, r, r,  )
        b1 = self.unitPolygon( m, r, dL, r, r, True )
        b1.reverse()
        ub = u1 + b1
        width, height = self.unitSize( ub )
        print(' Unit polygon size = %.2f, %.2f' %(width, height))

        return width, height


    # BL : bottom-left position, TR : top-right position
    def createPattern(self, BL, TR, n, m, r, dL  ):

        L = TR[0] - BL[0]
        H = TR[1] - BL[1]

        w0, h0 = self.unitPolygonSize( n, m, r, dL )
        h1 = h0 + self.bs

        nX = int(L / w0) + 1
        nY = int(H*2 / h1) + 1
        print(' nX = %d , nY = %d' %(nX, nY) )

        x = BL[0] + r
        y = TR[1] - (h0/2)
        arcs = []
        dx = (2*r) + dL
        dy = h1
        for j in range( nY ) :

            for i in range( nX ) :

                if j%2 == 0 :
                    u1 = self.unitPolygon( n, r, dL, x, y )
                    if i < nX-1 :
                        del u1[-1]
                        x = x + dx
                    arcs = arcs + u1
                else :
                    b1 = self.unitPolygon( m, r, dL, x, y, True )
                    b1.reverse()
                    if i < nX-1 :
                        del b1[-1]
                        x = x - dx
                    arcs = arcs + b1

            if j%2 == 0 :
                y = y - self.bs
            else :
                y = y - dy

        return arcs

    # BL : bottom-left position, TR : top-right position
    def createPatternX(self, BL, TR, n, m, r, dL, LR = True, UD = True  ):

        L = TR[0] - BL[0]
        H = TR[1] - BL[1]

        # This is the width and height when constructing polygon in 0 degree rotation
        # for the pattens lay vertically, the rotation angle is -pi/2
        w0, h0 = self.unitPolygonSize(n, m, r, dL )
        h1 = h0 + self.bs

        # Partition the space
        nX = int(L*2 / h1) + 1
        nY = int(H / w0) + 2
        print(' nX = %d , nY = %d' %(nX, nY) )

        # setup starting point and angle
        phi = math.pi/-2
        y = TR[1] - r
        dy = (2*r) + dL
        if UD is False :
            phi = math.pi/2
            y = BL[1] + r
            dy = (-2*r) - dL

        x = BL[0] + (h0/2)
        if LR is False :
            x = TR[0] - (h0/2)

        # setup the dx base on the routing
        dx1 = h1
        dx2 = self.bs
        if LR is False and UD is True :
            dx1 = -1*self.bs
            dx2 = -1*h1
        if LR is True and UD is False :
            dx1 = self.bs
            dx2 = h1
        if LR is True and UD is True :
            dx1 = h1
            dx2 = self.bs
        if LR is False and UD is False :
            dx1 = -1*h1
            dx2 = -1*self.bs


        arcs = []
        for j in range( nX ) :

            for i in range( nY ) :

                if j%2 == 0 :
                    u1 = self.unitPolygon( n, r, dL, x, y, False, phi  )
                    if i < nY-1 :
                        del u1[-1]
                        y = y - dy
                    arcs = arcs + u1
                else :
                    b1 = self.unitPolygon( m, r, dL, x, y, True, phi )
                    b1.reverse()
                    if i < nY-1 :
                        del b1[-1]
                        y = y + dy

                    arcs = arcs + b1

            if j%2 == 0 :
                x = x + dx1
            else :
                x = x + dx2

        return arcs

    def createSquareX(self, BL, TR, h, w, ds, dL, LR = True, UD = True  ):

        L = TR[0] - BL[0]
        H = TR[1] - BL[1]

        # This is the width and height when constructing square
        # for the pattens lay vertically, the rotation angle is -pi/2
        w0 = w + dL
        h1 = h

        # Partition the space
        nX = int(L / h1) + 2
        nY = int(H / w0) + 1
        print(' nX = %d , nY = %d' %(nX, nY) )

        # setup starting point and angle
        phi = math.pi/-2
        y = TR[1]
        dy = (-1*w) - dL
        if UD is False :
            phi = math.pi/2
            y = BL[1]
            dy = w + dL

        # setup the dx base on the routing
        x = BL[0]
        dx = h
        if LR is False :
            x = TR[0]
            dx = -1*h
        print(' dx = %.3f , dy = %.3f' %(dx, dy) )

        arcs = []
        for j in range( nX ) :

            for i in range( nY ) :

                if j%2 == 0 :
                   # def unitSquare(self, h, w, dL, x0, y0, ds = 0, phi = 0 ):
                    u1 = self.unitSquare( h, w, dL, x, y, ds, phi  )
                    if i < nY-1 :
                        del u1[-1]
                        y = y + dy
                    #print(' (%.3f,%.3f) from %.3f  to %.3f' %(x,y, u1[0][1], u1[-1][1] ) )
                    arcs = arcs + u1
                else :
                    b1 = self.unitSquare( h, w, dL, x, y, ds, phi )
                    b1.reverse()
                    if i < nY-1 :
                        del b1[-1]
                        y = y - dy
                    #print(' (%.3f,%.3f) from %.3f  to %.3f' %(x,y, b1[0][1], b1[-1][1] ) )

                    arcs = arcs + b1

            x = x + dx

        return arcs

    def createSquareY(self, BL, TR, h, w, ds, dL, UD = True, LR = True  ):

        L = TR[0] - BL[0]
        H = TR[1] - BL[1]

        # This is the width and height when constructing square
        # for the pattens lay vertically, the rotation angle is -pi/2
        w0 = w + dL
        h1 = abs(h)

        # Partition the space
        nX = int(L / w0) + 1
        nY = int(H / h1) + 2
        print(' nX = %d , nY = %d' %(nX, nY) )

        # setup starting point and angle
        y = TR[1] - h
        dy = -1*h1
        if UD is False :
            y = BL[1]
            dy = h1

        # setup the dx base on the routing
        x = BL[0]
        dx = w + dL
        phi = 0
        if LR is False :
            phi = math.pi
            x = TR[0]
            dx = -1*w - dL
        print(' dx = %.3f , dy = %.3f' %(dx, dy) )

        arcs = []
        for j in range( nY ) :

            for i in range( nX ) :

                if j%2 == 0 :
                    # def unitSquare(self, h, w, dL, x0, y0, ds = 0, phi = 0 ):
                    u1 = self.unitSquare( h, w, dL, x, y, ds, phi  )
                    if i < nX-1 :
                        del u1[-1]
                        x = x + dx
                    #print(' (%.3f,%.3f) from %.3f  to %.3f' %(x,y, u1[0][1], u1[-1][1] ) )
                    arcs = arcs + u1
                else :
                    b1 = self.unitSquare( h, w, dL, x, y, ds, phi )
                    b1.reverse()
                    if i < nX-1 :
                        del b1[-1]
                        x = x - dx
                    #print(' (%.3f,%.3f) from %.3f  to %.3f' %(x,y, b1[0][1], b1[-1][1] ) )

                    arcs = arcs + b1

            y = y + dy

        return arcs


    # if val == 0  -> colinear and r is between p and q
    #    val == 2  -> colinear and r is Outside p or q
    #    val == -1  -> clockwise
    #    val ==  1 -> counterclockwise
    def orientation(self, p, q, r ):

        # using cross-product to identify whether it's colinear or not
        #val = ( (q[1] - p[1])*(r[0] - q[0]) ) - ( (q[0]-p[0])*(r[1] - q[1]) )
        val = ( (q[1] - p[1])*(r[0] - p[0]) ) - ( (q[0]-p[0])*(r[1] - p[1]) )

        if val > 0.0000001  :
            return 1
        elif val < -0.0000001 :
            return -1
        else :
        #if val == 0 :
            if r[0] <= max(p[0], q[0]) and r[0] >= min(p[0], q[0]) and r[1] <= max(p[1], q[1]) and r[1] >= min( p[1],q[1] ) :
                return 0
            else :
                return 2


    # Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
    #    y = mx + d
    #  |y1| = | x1  1 | | m |
    #  |y2|   | x2  1 | | d |
    #   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
    # if it's a vertical line, d is set to be x value
    def solveLine(self, x1, y1, x2, y2):
        # to avoid m is infinit
        m = 999999999
        d = 0
        if x1 == x2 or abs(x1-x2) < 0.000001:
            d = (x1+x2)/2
        else :
            a = np.array([[x1, 1.], [x2, 1.]])
            b = np.array([y1, y2])
            c = np.linalg.solve(a, b)
            m = c[0]
            d = c[1]

        return m, d

    # Find intersect point x,y given 4 points
    def findIntersect(self, p1, q1, p2, q2 ):

        m1, d1 = self.solveLine(p1[0], p1[1], q1[0], q1[1])
        m2, d2 = self.solveLine(p2[0], p2[1], q2[0], q2[1])
        #print(' m1 = %.3f m2 = %.3f ' %(m1,m2))
        #print(' d1 = %.3f d2 = %.3f ' %(d1,d2))
        x = 0
        y = 0
        if m1 == 999999999 :
            x = d1
            y = (m2*x) + d2

        elif m2 == 999999999 :
            x = d2
            y = (m1*x) + d1

        else :
            if m1 == m2:
                print(' parallel segments !! m = %.3f ' %(m1))
                m1 = m1 * 1.0000001
                m2 = m2 * 0.9999999
            a = np.array([[m1, -1.], [m2, -1.]])
            b = np.array([-1 * d1, -1 * d2])
            c = np.linalg.solve(a, b)
            x = c[0]
            y = c[1]

        return x, y
        # print( '(%d,%d) = [ %.3f, %.3f ]' %( i, j, c[0], c[1]) )

    # return the intersection point
    def doIntersect(self, p1, q1, p2, q2 ):

        interlist = []

        if p2[0] == q2[0] and p2[1] == q2[1] :
            return interlist
        if p1[0] == q1[0] and p1[1] == q1[1] :
            return interlist


        # find out the 4 orientation
        # if val == 0  -> colinear p-r-q
        #    val == 2  -> colinear p-q-r  or r-p-q
        #    val == 1  -> clockwise, val == -1 -> counterclockwise
        o1 = self.orientation( p1, q1, p2 )
        o2 = self.orientation( p1, q1, q2 )
        o3 = self.orientation( p2, q2, p1 )
        o4 = self.orientation( p2, q2, q1 )

        colinear = False
        if  o1 == 0  or o2 == 0 or o3 == 0 or o4 ==0 :
            colinear = True
        if  o1 == 2  or o2 == 2 or o3 == 2 or o4 ==2 :
            colinear = True


        # General case  for intersection
        if o1 != o2 and o3 != o4 and colinear is False:
            x, y = self.findIntersect( p1, q1, p2, q2 )
            interlist.append( [x,y] )

        else :

            # special cases , one or two points are colinear
            # p1-p2-q2-q1,
            if o1 == 0 and o2 == 0 :
                interlist.append( p2 )
                interlist.append( q2 )
            # p2-p1-q1-q2,
            if o3 == 0 and o4 == 0 :
                interlist.append( p1 )

            if o1 == 0 and o2 != 0 and o3 != 0 and o4 != 0 :
                interlist.append( p2 )
            if o2 == 0 and o1 != 0 and o3 != 0 and o4 != 0 :
                interlist.append( q2 )
            if o3 == 0 and o1 != 0 and o2 != 0 and o4 != 0 :
                interlist.append( p1 )
            if o4 == 0 and o1 != 0 and o2 != 0 and o3 != 0 :
                interlist.append( q1 )

            #if abs(o1) == 1 and abs(o2) == 1 and o3 == 2 and o4 == 2 :
            # This is a situation where p2 and q2 are the same


        return interlist


    # arc is the pattern list, pos is the outline list
    def filterPattern(self, arc, pos ):

        # the element in this container is [x,y, stat]
        # stat = 0 -> inside polygon, stat = 1 -> outside polygon , given boundary point
        patV = []
        # loop all pattern point to check whether they are inside the boundary
        for i in range( len(arc) ) :

            itlist = []
            bList = []
            # form a horizental line
            qx = [999, arc[i][1]]
            p1 = arc[i]
            q1 = arc[i-1]
            for j in range( len(pos) ) :

                # testing outline segment
                p2 = pos[j-1]
                q2 = pos[j]

                # check to see if the point is inside the polygon
                testP = self.doIntersect( p1, qx, p2, q2 )
                if len(testP) > 0 :
                    itlist.append( testP )
                # check if the point across the boundary
                boundP = self.doIntersect( p1, q1, p2, q2 )
                if len(boundP) > 0 :
                    for it in boundP :
                        bList.append( [ it[0], it[1], j ] )

            # Add the boundary point
            if len(bList) > 0 :
                patV.append( [bList[0][0], bList[0][1], 1, bList[0][2] ] )

            # odd number of intersection means the point is inside the polygon
            if len(itlist)%2 == 1 :
                patV.append( [arc[i][0], arc[i][1], 0 ] )

        patF = []
        for i in range( len(patV) ):

            # whatever the 1st point or the inside points are collected
            if i == 0 or patV[i][2] == 0:
                patF.append( [patV[i][0], patV[i][1]] )
                continue

            # If two adjacent boundary points happen, connect them with outline points
            if patV[i][2] == 1 and patV[i-1][2] == 1 and i == 1:
                patF.append( [patV[i][0], patV[i][1]] )
            if patV[i][2] == 1 and patV[i-1][2] == 0 and i > 1:
                patF.append( [patV[i][0], patV[i][1]] )

            if patV[i][2] == 1 and patV[i-1][2] == 1 and i > 1:
                j = patV[i][3]
                k = patV[i-1][3]

                if abs(j-k+1) < abs(k-j+1) :
                    for m in range( abs(j-k+1) ) :
                        patF.append( [ pos[k-m-1][0], pos[k-m-1][1] ] )

                if abs(j-k+1) > abs(k-j+1) :
                    for m in range( abs(k-j+1) ) :
                        patF.append( [ pos[k+1+m][0], pos[k+1+m][1] ] )

                patF.append( [patV[i][0], patV[i][1]] )

        return patF


    def fillSpace(self, pos , n, m, r, dL, sx = 0, sy = 0  ):

        top, bott, left, right = self.findRange(pos)

        TR = [ right[0]+sx, top[1]+sy ]
        BL = [ left[0]+sx, bott[1]+sy ]

        #print( TR )
        #print( BL )

        # create the cutting boundary for filterPattern
        #cf = ConcentricFill()
        #cutb = cf.GetOutline( pos, -1*self.bs, False )

        arcs = self.createPattern( BL, TR, n, m, r, dL )
        print( ' len of arcs : %d' %( len(arcs) ) )
        patt = self.filterPattern( arcs, pos )
        print( ' len of patt : %d' %( len(patt) ) )

        return patt
        #return arcs


    def fillSpaceX(self, pos , n, m, r, dL, sx = 0, sy = 0, LR = False, UD = True    ):

        top, bott, left, right = self.findRange(pos)

        TR = [ right[0]+sx, top[1]+sy ]
        BL = [ left[0]+sx, bott[1]+sy ]

        # create the cutting boundary for filterPattern
        #cf = ConcentricFill()
        #cutb = cf.GetOutline( pos, -1*self.bs, False )

        arcs = self.createPatternX( BL, TR, n, m, r, dL, LR, UD )
        print( ' len of arcs : %d' %( len(arcs) ) )
        patt = self.filterPattern( arcs, pos )
        print( ' len of patt : %d' %( len(patt) ) )

        return patt
        #return arcs

    # Fill space with square pattern
    def fillSquareX(self, pos , h,w, ds, dL, sx = 0, sy = 0, LR = False, UD = True    ):

        # define space
        top, bott, left, right = self.findRange(pos)

        TR = [ right[0]+sx, top[1]+sy ]
        BL = [ left[0]+sx, bott[1]+sy ]

        # create the cutting boundary for filterPattern
        # createSquareX(self, BL, TR, h, w, ds, dL, LR = True, UD = True  ):
        arcs = self.createSquareX( BL, TR, h, w, ds, dL, LR, UD )
        print( ' len of arcs : %d' %( len(arcs) ) )
        #patt = self.filterPattern( arcs, pos )
        #print( ' len of patt : %d' %( len(patt) ) )

        #return patt
        return arcs


    def fillSquareY(self, pos , h,w, ds, dL, sx = 0, sy = 0, UD = True, LR = True    ):

        # define space
        top, bott, left, right = self.findRange(pos)

        TR = [ right[0]+sx, top[1]+sy ]
        BL = [ left[0]+sx, bott[1]+sy ]

        # create the cutting boundary for filterPattern
        # createSquareX(self, BL, TR, h, w, ds, dL, LR = True, UD = True  ):
        arcs = self.createSquareY( BL, TR, h, w, ds, dL, UD, LR )
        print( ' len of arcs : %d' %( len(arcs) ) )
        patt = self.filterPattern( arcs, pos )
        print( ' len of patt : %d' %( len(patt) ) )

        return patt
        #return arcs
