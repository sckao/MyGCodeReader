import math
from PolygonFill import PolygonFill

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
        while y >= (yc - r + self.bs ) :

            xr = math.sqrt( (r*r) - (yr*yr) )
            x1 = xc - xr*pow(-1,i)
            x2 = xc + xr*pow(-1,i)

            # construct connecting arc
            if i > 0 :
                arcV = self.getPolygon( 3, pV[-1], [x1 ,y], xc, yc )
                for it in arcV :
                    it.append(0)
                    pV.append( it )

            pV.append( [ x1, y]  )
            pV.append( [ x2, y]  )

            # move downward
            y = y - dy
            yr = abs( y - yc )
            i = i+1


        return pV

    def polygonFillCircle(self, xc, yc, r, delta, n, m, ds, dL, arcSpace = 1   ):

        poly = PolygonFill()
        w0, h0 = poly.unitSize( ds, dL, n, m )
        print('w: %.3f , h: %.3f' %(w0,h0) )

        # 0. decide the starting point
        yr = r - delta
        y0 = yc + yr
        x0 = xc - w0 + (dL/2)
        dx = abs(ds) + dL
        print(' x0 :%.3f y0:%.3f' %(x0, y0) )

        pV = []

        i = 0
        y = y0
        dy = poly.beadwidth*arcSpace
        while y >= (yc - r + h0 ) :

            yr = abs(y - yc)
            xr = math.sqrt( (r*r) - (yr*yr) )
            # 1. Decide the boundary
            x1 = xc - xr*pow(-1,i)
            x2 = xc + xr*pow(-1,i)
            # 1.1 adjust right end position
            #if i%2 == 0 :
                #x2 = x2 - (self.bs/2)
            #    x2 = x2 + (0.45*self.bs)
            #if i%2 == 1 :
                #x1 = x1 - (self.bs/2)
            #    x1 = x1 + (0.45*self.bs)

            # 2. Decide the starting point of each line
            if abs(x0 - x1) > ( dx + dL):
                m = int((x1-x0)/dx)
                x0 = x0 + m*dx

            # 2.1 if x0 is too closed to the boundary , backup
            if abs(x0 - x1) < dL :
                if i%2 == 0 :
                    x0 = x0 + dx
                if i%2 == 1 :
                    x0 = x0 - dx

            # 2.2 if x0 is out of the boundary , backup
            if i%2 == 0 and x0 < x1 :
                x0 = x0 + dx
            if i%2 == 1 and x0 > x1 :
                x0 = x0 - dx

            # 2.3 construct connecting arc
            if i%2 == 0 and i > 0 :
                arcV = self.getPolygon( 3, pV[-1], [x1 ,y], xc, yc )
                for it in arcV :
                    it.append(0)
                    pV.append( it )


            # 3. Create half arc
            print('(%d) y = %.3f , [%.3f - %.3f - %.3f] ' %(i, y, x1, x0, x2))
            poly.createLine( pV, [x1, y], [x2,y], [x0,y] , ds*pow(-1,i), dL, n  )

            # 4. move downward
            if i%2 == 0 :
                y = y - dy
                x0 = xc + abs(xc -x0 )
            else :
                y = y - h0 - dy
                x0 = xc - abs(xc -x0)

            i = i+1

        # create final circle to round around
        #rf = math.sqrt( (pV[0][0]-xc)*(pV[0][0]-xc)  + (pV[0][1]-yc)*(pV[0][1]-yc) )
        #Af = math.acos((pV[0][0] - xc) / rf)
        #xf = rf*math.cos(Af*1.04) + xc
        #yf = rf*math.sin(Af*1.04) + yc
        #fArc = poly.createPolygon(50, pV[-1], [xf,yf], xc, yc )
        #fArc = poly.createPolygon(50, pV[-1], pV[0], xc, yc )
        #for it in fArc :
        #    pV.append( it )

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
                # a hack to set eval to 0 for intermediate point
                if len(pV[i]) > 2 and pV[i][2] == 0 :
                    eval = 0

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


    # Define a rectangle area from the printing outlines
    def defineRange(self, pos ):

        top  = [ pos[0][0], pos[0][1] ]
        bott = [ pos[0][0], pos[0][1] ]
        left = [ pos[0][0], pos[0][1] ]
        right= [ pos[0][0], pos[0][1] ]

        for it in pos :

            if it[1] > top[1] :
                top = [ it[0], it[1] ]
            if it[1] < bott[1] :
                bott = [ it[0], it[1] ]
            if it[0] > left[0] :
                right = [ it[0], it[1] ]
            if it[0] < right[0] :
                left = [ it[0], it[1] ]

        return top,bott,left,right



    # Find left and right boundary
    # dY > 0 means upper arc , dY < 0 means lower arc
    def findBoundary(self, theY, dY, minY, maxY, pos):

       x1 = 0.
       x2 = 0.
       x1s = 0.
       x2s = 0.
       Y_s = theY + dY
       if Y_s < minY or Y_s > maxY :
           return x1,x2,x1s,x2s

       for i in range( len(pos)-1 )  :

           if theY < pos[i][1] and theY > pos[i+1][1] :
               x1 = pos[i][0] - ((pos[i][0] - pos[i+1][0])*( pos[i][1] - theY )/( pos[i][1]-pos[i+1][1]) )
           if theY > pos[i][1] and theY < pos[i+1][1] :
               x2 = pos[i][0] - ((pos[i][0] - pos[i+1][0])*( pos[i][1] - theY )/( pos[i][1]-pos[i+1][1]) )

           if Y_s < pos[i][1] and Y_s > pos[i+1][1] :
               x1s = pos[i][0] - ((pos[i][0] - pos[i+1][0])*( pos[i][1] - Y_s )/( pos[i][1]-pos[i+1][1]) )
           if Y_s > pos[i][1] and Y_s < pos[i+1][1] :
               x2s = pos[i][0] - ((pos[i][0] - pos[i+1][0])*( pos[i][1] - Y_s )/( pos[i][1]-pos[i+1][1]) )

           if x1 != 0. and x2 != 0 and x1s != 0 and x2s != 0 :
               break

       xL = min(x1,x2)
       xR = max(x1,x2)
       xLs = min(x1s,x2s)
       xRs = max(x1s,x2s)
       print( ' xL: %.2f, xR: %.2f, xLs: %.2f, xRs: %.2f ' %( xL, xR, xLs, xRs) )

       return xL, xR, xLs, xRs

    def startX(self, width, ranges, boundary, toLeft = False ):

        x0 = min(ranges)
        if toLeft :
            x0 = max(ranges)

        n = abs( ranges[1] - ranges[0] )/width
        m = int(n)
        print( ' n = %d , x0 = %.2f' %(m, x0))

        for i in range(m) :

            if toLeft :

                if x0 > max(boundary) :
                    x0 = x0 - width
                    continue
                else :
                    x0 = x0 + width
                    break
            else :

                if x0 < min(boundary)  :
                    x0 = x0 + width
                    continue
                else :
                    x0 = x0 - width
                    break

        print(' x0 = %.2f ' %(x0))
        return x0



    def FillArbitrary(self, pos, ds, dL, n, m):

        poly = PolygonFill()
        # determine the unit polygon size
        w0, h0 = poly.unitSize(ds, dL, n, m)
        h0 = h0
        print('w: %.3f , h: %.3f' % (w0, h0))

        # Find the top,bottom, left and right range
        top,bott,left,right = self.defineRange(pos)
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(top[1], bott[1], left[0], right[0]))
        # Partition the rectangle space
        nX = int( (right[0] - left[0]) / w0 ) + 1
        nY = int( (top[1]   - bott[1]) / h0 ) + 1
        print( 'NX: %d , NY: %d' %(nX, nY) )
        # Re-define the range of partition space
        deltaX = (nX*w0) - ( right[0] - left[0] )
        xRange = [ left[0]-(deltaX/2) , right[0]+(deltaX/2) ]
        deltaY = (nY*h0) - ( top[1] - bott[1] )
        yRange = [ top[1] + (deltaY/2), bott[1] - (deltaY/2) ]
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(yRange[0], yRange[1], xRange[0], xRange[1]))
        # setup starting Y and X position (x0,y0)
        y0 = yRange[0] - (h0)

        dy = h0/2
        y = y0
        arcV = []
        i=0
        while y > bott[1] :

            print( '(%d) Y = %.3f ' %( i, y ) )
            xL,xR,xLs,xRs = self.findBoundary( y, dy*pow(-1,i), bott[1], top[1], pos )

            if i%2 == 0:
                x = self.startX( w0, xRange, [xL,xR] )
                poly.createLineNew( arcV, x, y, xL, xR, xLs, xRs, ds*pow(-1,i), dL, n, 1 )
                y = y - poly.beadwidth
            else:
                x = self.startX( w0, xRange, [xL,xR], True )
                poly.createLineNew( arcV, x, y, xR, xL, xRs, xLs, ds*pow(-1,i), dL, n, 1 )
                y = y - h0 - poly.beadwidth

            i = i+1


        return arcV




