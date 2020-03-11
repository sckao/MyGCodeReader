import math

class Fill3D :

    def __init__(self):
        self.dzdx = 1.
        self.dzdy = 1.
        self.z0 = 0
        self.x0 = 0
        self.y0 = 0

    def setReferenceXY(self, x0, y0 ):
        self.x0 = x0
        self.y0 = y0

    def ApplyContour(self, contourV, x, y):

        dx0 = -99999
        dy0 = -99999
        for i in range( len( contourV )) :

            if contourV[i][0] < x and contourV[i][1] < y :
                dx0 = contourV[i][0] - x
                dy0 = contourV[i][1] - y



    def dzdr(self, dx, dy ):

        dz = (self.dzdx*dx) + (self.dzdy*dy)

        return dz


    # In order to get the proper z height, the reference X,Y need to be set
    def getGcode(self, pV , zVal=0, rs=[], rx=[], ry=[], rz=[], rE=[], stat = 1, slope = True ):

        # deltaZ for starting
        deltaZ = 0.15
        rampL = 5
        zH = zVal

        printL = 0
        for i in range(len(pV)):

            if i == 0:

                dx = pV[i][0] - self.x0
                dy = pV[i][1] - self.y0
                dz = self.dzdr( dx, dy )
                if stat == 1 and slope is True :
                    zH = zVal - deltaZ + dz
                else :
                    zH = zVal + dz
                rx.append(pV[i][0])
                ry.append(pV[i][1])
                rz.append(zH)
                rs.append(0)
                rE.append(0)

            else:
                dx = pV[i][0] - pV[i - 1][0]
                dy = pV[i][1] - pV[i - 1][1]
                dz = self.dzdr( dx, dy )
                dL = math.sqrt( (dx*dx) + (dy*dy) + (dz*dz) )
                dt = dL / self.Fval
                eval = self.Eval * dt
                # a hack to set eval to 0 for intermediate point
                if len(pV[i]) > 2 and pV[i][2] == 0 :
                    eval = 0

                printL += dL
                if printL < 5 and stat != 5 and slope is True :
                    zH = zH + (deltaZ*printL/rampL) + dz
                    if zH > zVal :
                        zH = zVal
                else :
                    zH = zVal + dz

                rx.append( pV[i][0] )
                ry.append( pV[i][1] )
                rz.append(zH)
                rs.append(stat)
                rE.append(eval)
