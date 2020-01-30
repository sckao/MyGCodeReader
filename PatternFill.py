import math
import numpy as np


class PatternFill :

    def __init__(self):

        self.bw = 1.75
        self.bsScale = 0.5
        self.bs = self.bw*self.bsScale
        self.yScale = 1.

    def setBeadSpace(self, bw, bsscale ):

        self.bw = bw
        self.bsScale = bsscale

    # providing shapes from left to right
    def unitPolygon(self, n, r, dL, x0, y0, flip = False ) :

        pattern = []
        dA = math.pi / (n+1)

        theta = math.pi
        x = x0
        y = y0
        for i in range(n+2) :
            dx = r*math.cos( theta )
            dy = r*math.sin( theta )
            x = x0 + r + dx
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

        width = left[0] - right[0]
        height = top[1] - bott[1]

        return width, height

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

    def doIntersect(self, p1, q1, p2, q2 ):

        interlist = []
        # find out the 4 orientation
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
            # p1, q1, p2 are colinear and p2 is between p1 and q1
            if o1 == 0 and o2 == 0 :
                interlist.append( p2 )
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


    def inRangeCheck(self, arc, pos ):

        patV = []
        for i in range( len(arc) ) :

            for j in range( len(pos) ) :

                p1 = arc[i]
                q1 = [999, arc[i][1]]

                p2 = pos[j-1]
                q2 = pos[j]
                itlist = self.doIntersect( p1, q1, p2, q2 )

                # odd number of intersection means the point is inside the polygon
                if len(itlist)%2 == 1 :
                    patV.append( arc[i] )
                else :











    def fillSpace(self, pos):

        beadSpacing = self.BSScale * self.beadWidth

        # set up pattern type
        # n =2 , r =4, dL =4 , (x0,y0) = (0,0)
        pattern0  = self.unitPolygon(2,4,4,0,0)

        # determine the unit polygon size
        w0, h0 = self.unitSize( pattern0 )
        h0 = (h0 * self.yScale) + beadSpacing
        print('w: %.3f , h: %.3f' % (w0, h0))

        # Find the top,bottom, left and right range
        top, bott, left, right = self.find(pos)
        print('Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' % (top[1], bott[1], left[0], right[0]))
        # Partition the rectangle space
        nX = int((right[0] - left[0]) / w0) + 1
        nY = int((top[1] - bott[1]) / (h0 + beadSpacing)) + 1
        print('NX: %d , NY: %d' % (nX, nY))

        # Determine starting point
        x = left[0]
        y = top[1] - h0
        flip = False
        fillV = []
        for j in range( nY ) :

            # Layout the pattern in the partition range
            if j%2 == 1 :
                flip = True
            for i in range( nX ) :
                patt_i = self.unitPolygon(2,4,4,x, y, flip)
                if flip is True :
                    patt_i.reverse()

                fillV = fillV + patt_i
                x = x + w0

            # Check the pattern whether they are in the range
            for k in range( len(pos) ) :

                if pos[k][1] <= y and pos[k][1] > (y+h) :
                    continue

                x1 = pos[k][0]
                y1 = pos[k][1]




            y = y - h0