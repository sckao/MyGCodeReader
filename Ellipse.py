import math

class Ellipse :

    def __init__(self, a_ , b_, x_0, y_0 ):

        self.a = a_
        self.b = b_
        self.x0 = x_0
        self.y0 = y_0

    def getR(self, theta ):

        asin = self.a*math.sin( theta )
        bcos = self.b*math.cos( theta )
        r = (self.a*self.b) / math.sqrt( (asin*asin) + (bcos*bcos) )

        return r

    def getEllipse(self, n = 40 ):

        pathV = []
        theta = 0
        for i in range(n) :

            dTheta = 2*math.pi/ n

            r = self.getR( theta )
            x = r*math.cos(theta) + self.x0
            y = r*math.sin(theta) + self.y0
            pathV.append( [x,y] )

            theta = theta + dTheta

        x1 = pathV[0][0]
        y1 = pathV[0][1]
        pathV.append( [x1,y1] )

        return pathV
