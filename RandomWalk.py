import math


class RandomWalk :


    def __init__(self):

        self.phi = []
        self.r = []
        self.u =[]
        self.v = []


    def createUnit(self, x, y ):

        for i in range( len(r) ) :

            dx = self.r[i] * math.cos( self.phi[i] )
            dy = self.r[i] * math.sin( self.phi[i] )
            x = x + dx
            y = y + dy

            self.u.append( x )
            self.v.append( v )
