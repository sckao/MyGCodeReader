import math
import numpy as np

class PointInPolygon :

    def __init__(self):

        self.polygon = []

    # Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
    #   ny = mx + d
    #  |y1| = | x1  1 | | m |
    #  |y2|   | x2  1 | | d |
    #   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d,n]
    def solveLine(self, x1, y1, x2, y2):

        r = []
        if x1 == x2 :
            r = [1, -1*x1, 0 ]

        else :
            a = np.array([[x1, 1.], [x2, 1.]])
            b = np.array([y1, y2])
            c = np.linalg.solve(a, b)
            r = [c[0], c[1], 1 ]

        return r


    # Find the intercept point between line(p,r) and line( y = q.y )
    # segment points: p,  r
    # testing point : q
    def onSegment(self, p , r, q ):

        intcP = []
        #  q.y is larger than p.y or r.y or smaller than p.y or r.y , skipped
        if q[1] > max( p[1], r[1] ) or q[1] < min(p[1],r[1]) :
            return intcP

        # q.x is larger than p.x and r.x , skipped
        elif q[0] > max( p[0], r[0] ) :
            return intcP

        # Solve the intersection
        else :

            m = self.solveLine( p[0], p[1], r[0], r[1])

            if m[2] == 0 :
               xc = -1*m[1]
               yc = q[1]
               intcP = [xc, yc]

            else :
               # x = (y - d)/m
               xc = (q[1] - m[1])/m[0]
               yc = q[1]
               intcP = [xc, yc]


            return intcP

    def intercept(self, p, r , q ):

        intcp = self.onSegment(p,r,q)

        if len(intcp) < 2 :
            return False

        else :

            if intcp[0] < q[0] :
                return False
            else :
                return True


