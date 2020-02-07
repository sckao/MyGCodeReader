import math
import numpy as np

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

    # providing shapes from left to right
    # n: number of point in upper/bottom half, radius, dL : spacing
    # flip : upper or bottom half of the polygon
    # return points
    def unitPolygon(self, n, r, dL, x0, y0, flip = False ) :

        pattern = []
        dA = math.pi / (n+1)

        theta = math.pi
        x = x0
        y = y0
        for i in range(n+2) :
            dx = r*math.cos( theta )
            dy = r*math.sin( theta )
            x = x0 + dx
            if flip is True :
                y = y0 - dy
            else :
                y = y0 + dy
            pattern.append( [x,y] )
            theta = theta - dA

        pattern.append( [x+dL, y0] )
        return pattern

    def unitSquare(self, h, w, dL, x0, y0):

        pattern = []

        pattern.append( [x0, y0] )
        pattern.append( [x0, y0+h] )
        pattern.append( [x0+w, y0+h] )
        pattern.append( [x0+w, y0] )
        pattern.append( [x0+w+dL, y0] )

        return pattern

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
                    arcs = arcs + b1
                    if i < nX-1 :
                        x = x - dx

            if j%2 == 0 :
                y = y - self.bs
            else :
                y = y - dy

        return arcs


    # if val == 0  -> colinear and r is between p and q
    #    val == 2  -> colinear and r is Outside p or q
    #    val == 1  -> clockwise
    #    val == -1 -> counterclockwise
    def orientation(self, p, q, r ):

        val = ( (q[1] - p[1])*(r[0] - q[0]) ) - ( (q[0]-p[0])*(r[1] - q[1]) )


        if val == 0 :

            if r[0] <= max(p[0], q[0]) and r[0] >= min(p[0], q[0]) and r[1] <= max(p[1], q[1]) and r[1] >= min( p[1],q[1] ) :
                return 0
            else :
                return 2

        if val > 0  :
            return 1
        if val < 0 :
            return -1

    # Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
    #    y = mx + d
    #  |y1| = | x1  1 | | m |
    #  |y2|   | x2  1 | | d |
    #   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
    def solveLine(self, x1, y1, x2, y2):
        # to avoid m is infinit
        if x1 == x2:
            x2 = x2 * 0.999999
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
        if m1 == m2:
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
        # find out the 4 orientation
        # if val == 0  -> colinear p-r-q
        #    val == 2  -> colinear p-q-r  or r-p-q
        #    val == 1  -> clockwise, val == -1 -> counterclockwise
        o1 = self.orientation( p1, q1, p2 )
        o2 = self.orientation( p1, q1, q2 )
        o3 = self.orientation( p2, q2, p1 )
        o4 = self.orientation( p2, q2, q1 )

        # General case  for intersection
        if o1 != o2 and o3 != o4 :
            x, y = self.findIntersect( p1, q1, p2, q2 )
            interlist.append( [x,y] )

        else :

            # special cases , one or two points are colinear
            # p1-p2-q2-q1,
            if o1 == 0 and o2 == 0 :
                interlist.append( p2 )
            # p2-p1-q1-q2,
            if o1 == 3 and o4 == 0 :
                interlist.append( p1 )

            if o1 == 0 and o2 != 0 and o3 != 0 and o4 != 0 :
                interlist.append( p2 )
            if o2 == 0 and o1 != 0 and o3 != 0 and o4 != 0 :
                interlist.append( q2 )
            if o3 == 0 and o1 != 0 and o2 != 0 and o4 != 0 :
                interlist.append( p1 )
            if o4 == 0 and o1 != 0 and o2 != 0 and o3 != 0 :
                interlist.append( q1 )

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
            if patV[i][2] == 1 and patV[i-1][2] == 1 and i > 1:
                j = patV[i][3]
                k = patV[i-1][3]

                if abs(j-k+1) < abs(k-j+1) :
                    for m in range( abs(j-k+1) ) :
                        patF.append( [ pos[k-m-1][0], pos[k-m-1][1] ] )

                if abs(j-k+1) > abs(k-j+1) :
                    for m in range( abs(k-j+1) ) :
                        patF.append( [ pos[k+1+m][0], pos[k+1+m][1] ] )

        return patF


    def fillSpace(self, pos , n, m, r, dL, sx = 0, sy = 0  ):

        top, bott, left, right = self.findRange(pos)

        TR = [ right[0]+sx, top[1]+sy ]
        BL = [ left[0]+sx, bott[1]+sy ]

        #print( TR )
        #print( BL )

        arcs = self.createPattern( BL, TR, n, m, r, dL )
        print( ' len of arcs : %d' %( len(arcs) ) )
        patt = self.filterPattern( arcs, pos )
        print( ' len of patt : %d' %( len(patt) ) )

        return patt
