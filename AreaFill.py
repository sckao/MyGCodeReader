import math

class AreaFill :

    def __init__(self):
        # do nothing
        self.Fval = 500.
        self.rho = 0.8
        self.rd = 5.0

    # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh) and retract distance (rd)
    def setTipHeight(self, ts0=0.35, bh0=0.5, fh0=0.1, rd0 = 5):
        self.ts = ts0
        self.bh = bh0
        self.fh = fh0
        self.rd = rd0
        self.z0 = self.ts + self.bh + self.fh
        return self.z0

    def setPrintable(self, fval, rho, bs ) :

        self.Fval = fval
        self.rho = rho
        self.bs = bs
        self.Eval = self.Fval* self.rho


    def LineFillCircle(self, xc, yc, r, dy):

        yr = r - dy
        y = yc + yr

        pV = []

        i = 0
        while y >= (yc - r ) :

            xr = math.sqrt( (r*r) - (yr*yr) )
            x1 = xc - xr*pow(-1,i)
            x2 = xc + xr*pow(-1,i)

            # construct connecting arc
            if i > 0 :
                arcV = self.getPolygon( 3, pV[-1], [x1 ,y], xc, yc )
                for it in arcV :
                    pV.append( it )

            pV.append( [ x1, y]  )
            pV.append( [ x2, y]  )

            # move downward
            y = y - dy
            yr = abs( y - yc )
            i = i+1


        return pV


    def getPolygon(self, nside, iniPos, endPos, xc, yc):

        # Getting initial radius ri and ending radius rj
        # Initial/ending angle in the range of 0 ~ 2pi
        ri = math.sqrt(((xc - iniPos[0]) * (xc - iniPos[0])) + ((yc - iniPos[1]) * (yc - iniPos[1])))
        rj = math.sqrt(((xc - endPos[0]) * (xc - endPos[0])) + ((yc - endPos[1]) * (yc - endPos[1])))
        iniA = math.acos((iniPos[0] - xc) / ri)
        endA = math.acos((endPos[0] - xc) / rj)
        if iniPos[1] < yc:
            iniA = (math.pi * 2) - iniA
        if endPos[1] < yc:
            endA = (math.pi * 2) - endA

        R = ri
        dR = (rj - ri) / nside
        arcV = []
        dPhi = (endA - iniA) / nside

        for i in range(nside):
            Phi = iniA + (i * dPhi)
            x = R * math.cos(Phi) + xc
            y = R * math.sin(Phi) + yc
            arcV.append([x, y])
            R = R + dR

        return arcV

    def getResult(self, pV , zVal=0, rs=[], rx=[], ry=[], rz=[], rE=[], retract=True):

        for i in range(len(pV)):

            # Calculate Eval
            prime_eval = 0.1
            retract_eval = -1
            shift_eval = -1
            if i == 0:

                if retract:
                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zVal + self.rd)
                    rs.append(0)
                    rE.append(shift_eval)

                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zVal)
                    rs.append(-2)
                    rE.append(prime_eval)
                else:
                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zVal)
                    rs.append(0)
                    rE.append(shift_eval)


            else:
                dx = pV[i][0] - pV[i - 1][0]
                dy = pV[i][1] - pV[i - 1][1]
                dt = math.sqrt((dx * dx) + (dy * dy)) / self.Fval
                eval = self.Eval * dt

                rx.append( pV[i][0] )
                ry.append( pV[i][1] )
                rz.append(zVal)
                rs.append(1)
                rE.append(eval)

            i = i + 1

        if retract:
            rx.append( pV[i - 1][0] )
            ry.append( pV[i - 1][1] )
            rz.append(zVal + self.rd)
            rs.append(2)
            rE.append(retract_eval)



    # FIXME : Not finished yet
    def sortsegment(self, xV, yV, dY  ):

        xc = sum(xV) / len(xV)
        yc = sum(yV) / len(yV)
        iniY = max( yV ) - self.bs
        endY = min( yV ) + self.bs

        # separate right and left segments
        LV = []
        RV = []
        for i in range( len(xV) ) :

            if xV[i] < xc :
                LV.append( [ xV[i], yV[i] ] )
            else :
                RV.append( [ xV[i], yV[i] ] )

        y = iniY
        dyP =   999999.
        dyM = - 999999.
        Lu = -1
        Ld = -1
        for i in range( len(LV) ) :

            dy = LV[i][1] - y
            if dy > 0 and dy < dyP :
                dyP = LV[i][1] - y
                Lu = i
            if dy < 0 and dy > dyM :
                dyM = LV[i][1] - y
                Ld = i


        y = iniY
        dyP =   999999.
        dyM = - 999999.
        Lu = -1
        Ld = -1
        for i in range( len(LV) ) :

            dy = LV[i][1] - y
            if dy > 0 and dy < dyP :
                dyP = LV[i][1] - y
                Lu = i
            if dy < 0 and dy > dyM :
                dyM = LV[i][1] - y
                Ld = i






