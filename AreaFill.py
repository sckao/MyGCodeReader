import math
from PolygonFill import PolygonFill
from PolygonFill import SolveLine
from PolygonFill import Intersection
from operator import itemgetter

class AreaFill:

    def __init__(self):
        # do nothing
        self.Fval = 500.
        self.rho = 0.8
        self.rd = 5.0
        self.yScale = 1.
        self.BSScale = 1.
        self.beadWidth = 1.75
        self.partition_dx = 0
        self.partition_dy = 0

    # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh) and retract distance (rd)
    def setTipHeight(self, ts0=0.35, bh0=0.5, fh0=0.1, rd0 = 10):
        self.ts = ts0
        self.bh = bh0
        self.fh = fh0
        self.rd = rd0
        self.z0 = self.ts + self.bh + self.fh
        return self.z0

    def setPrintable(self, fval, rho, bs ):

        self.Fval = fval
        self.rho = rho
        self.bs = bs
        self.Eval = self.Fval* self.rho

    # the scale of bead spacing , in unit of bead width
    def setBeadSpacing(self, bw, bs_scale):
        self.BSScale = bs_scale
        self.beadWidth = bw


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

    # state = 99 which means purge and wipe
    # use rE to store purge time
    def doPurge(self, purgeTime = 5. , rs=[], rx=[], ry=[], rz=[], rE=[], nextX = 0, nextY = 0   ):

        rx.append( nextX )
        ry.append( nextY )
        rz.append( 35 )
        rs.append( 99 )
        rE.append( purgeTime )

    def doRetract(self, p1, z1, p2, z2, connectV=[], rs=[], rx=[], ry=[], rz=[], rE=[] ):

        prime_eval = 0.1
        retract_eval = -3
        shift_eval = -1

        rx.append(p1[0])
        ry.append(p1[1])
        rz.append(z1 + self.rd )
        rs.append(2)
        rE.append(retract_eval)

        for i in range( len(connectV) ) :
            rx.append( connectV[i][0])
            ry.append( connectV[i][1])
            rz.append(z1 + self.rd)
            rs.append(0)
            rE.append(shift_eval)

        rx.append(p2[0])
        ry.append(p2[1])
        rz.append(z2 + self.rd)
        rs.append(0)
        rE.append(shift_eval)

        rx.append(p2[0])
        ry.append(p2[1])
        rz.append(z2)
        rs.append(-2)
        rE.append(prime_eval)


    def doLeakout(self, p1, z1, p2, z2, connectV=[], rs=[], rx=[], ry=[], rz=[], rE=[] ):

        retract_eval = 0
        shift_eval = -1
        # Get the total length
        L = 0
        for i in range( len(connectV) ) :

            dx = connectV[i][0] - connectV[i-1][0]
            dy = connectV[i][1] - connectV[i-1][1]
            if i == 0 :
                dx = connectV[i][0] - p1[0]
                dy = connectV[i][1] - p1[1]
            dL = math.sqrt( (dx*dx) + (dy*dy) )
            L = L + dL

        dz0 = (z2 - z1) / L


        rx.append(p1[0])
        ry.append(p1[1])
        rz.append(z1 )
        rs.append(2)
        rE.append(retract_eval)

        for i in range( len(connectV) ) :
            dx = connectV[i][0] - connectV[i-1][0]
            dy = connectV[i][1] - connectV[i-1][1]
            if i == 0 :
                dx = connectV[i][0] - p1[0]
                dy = connectV[i][1] - p1[1]
            dL = math.sqrt( (dx*dx) + (dy*dy) )
            dz = dz0* dL

            z1 = z1 + dz
            rx.append( connectV[i][0])
            ry.append( connectV[i][1])
            rz.append( z1 )
            rs.append(0)
            rE.append(shift_eval)

        rx.append(p2[0])
        ry.append(p2[1])
        rz.append(z2 )
        rs.append(0)
        rE.append(shift_eval)


    def getGcode(self, pV , zVal=0, rs=[], rx=[], ry=[], rz=[], rE=[], stat = 1, slope = True ):

        # deltaZ for starting
        deltaZ = 0.15
        rampL = 5
        zH = zVal

        printL = 0
        for i in range(len(pV)):

            if i == 0:

                if stat == 1 and slope is True :
                    zH = zVal - deltaZ
                else :
                    zH = zVal
                rx.append(pV[i][0])
                ry.append(pV[i][1])
                rz.append(zH)
                rs.append(0)
                rE.append(0)
            else:
                dx = pV[i][0] - pV[i - 1][0]
                dy = pV[i][1] - pV[i - 1][1]
                dL = math.sqrt((dx * dx) + (dy * dy))
                dt = dL / self.Fval
                eval = self.Eval * dt
                # a hack to set eval to 0 for intermediate point
                if len(pV[i]) > 2 and pV[i][2] == 0 :
                    eval = 0

                printL += dL
                if printL < 5 and stat != 5 and slope is True :
                    zH = zH + (deltaZ*printL/rampL)
                    if zH > zVal :
                        zH = zVal
                else :
                    zH = zVal

                rx.append( pV[i][0] )
                ry.append( pV[i][1] )
                rz.append(zH)
                rs.append(stat)
                rE.append(eval)



    def getResult(self, pV , zVal=0, rs=[], rx=[], ry=[], rz=[], rE=[], retract=True, stat = 1):

        # deltaZ for starting
        deltaZ = 0.15
        rampL = 5
        zH = zVal

        printL = 0
        for i in range(len(pV)):

            # Calculate Eval
            prime_eval = 0.1
            retract_eval = -3
            shift_eval = -1

            if i == 0:

                zH = zVal - deltaZ

                if retract:
                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zVal + self.rd)
                    rs.append(0)
                    rE.append(shift_eval)

                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zH)
                    rs.append(-2)
                    rE.append(prime_eval)
                else:
                    rx.append(pV[i][0])
                    ry.append(pV[i][1])
                    rz.append(zH)
                    rs.append(0)
                    rE.append(shift_eval)


            else:
                dx = pV[i][0] - pV[i - 1][0]
                dy = pV[i][1] - pV[i - 1][1]
                dL = math.sqrt((dx * dx) + (dy * dy))
                dt = dL / self.Fval
                eval = self.Eval * dt
                # a hack to set eval to 0 for intermediate point
                if len(pV[i]) > 2 and pV[i][2] == 0 :
                    eval = 0

                printL += dL
                if printL < 5 :
                    zH = zH + (deltaZ*printL/rampL)
                    if zH > zVal :
                        zH = zVal
                else :
                    zH = zVal

                rx.append( pV[i][0] )
                ry.append( pV[i][1] )
                rz.append(zH)
                rs.append(stat)
                rE.append(eval)

            #i = i + 1

        if retract and len(pV) > 0 :
            rx.append( pV[ -1][0] )
            ry.append( pV[ -1][1] )
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
            if it[0] > right[0] :
                right = [ it[0], it[1] ]
            if it[0] < left[0] :
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

    # Find left and right boundary and their corresponding segments
    # return a list of X boundaries , [ x_position, segment i of outline, segment j of outline ]
    def findXBoundary(self, theY, pos):

        xBlist = []
        #print( ' Find XBoundary for Y = %.2f' %(theY) )
        for i in range( len(pos) )  :
            j = i+1
            if j == len(pos) :
               j = 0
            #print( ' y = %.2f , seg Y_i = %.2f , Y_i+1 = %.2f ' %( theY, pos[i][1], pos[i+1][1] ) )
            if theY == pos[i][1] :
                x = pos[i][0]
                b = [x, i, j]
                xBlist.append( b )

            if theY < pos[i][1] and theY > pos[j][1] :
                m = (pos[i][0] - pos[j][0]) / ( pos[i][1]-pos[j][1])
                x = pos[i][0] - ( m*( pos[i][1] - theY ) )
                b = [ x, i, j ]
                xBlist.append( b )
            if theY > pos[i][1] and theY < pos[j][1] :
                m = (pos[j][0] - pos[i][0]) / ( pos[j][1]-pos[i][1])
                x = pos[i][0] - ( m*( pos[i][1] - theY ) )
                b = [ x, j, i ]
                xBlist.append( b )


        #print( 'x boundary list size %d' %( len(xBlist) ) )
        #if len(xBlist) == 1 :
        #    for i in range( len(pos)-1 )  :
        #        print( ' y = %.2f , seg Y_i = %.2f , Y_i+1 = %.2f ' %( theY, pos[i][1], pos[i+1][1] ) )

        #print( ' X Boundary => at y = %.2f , x1: %.2f, x2: %.2f ' %( theY, x1, x2) )

        xSortList = sorted( xBlist, key=itemgetter(0) )

        return xSortList

    # Given the X, finding Y boundary and the crossing segment
    # return a list of Y boundaries , [ y_position, segment i of outline, segment j of outline ]
    def findYBoundary(self, theX, pos):

        yBlist = []
        for i in range( len(pos) )  :
            j = i+1
            if j == len(pos) :
                j = 0
            if theX == pos[i][0]  :
                y = pos[i][1]
                b = [y, i, j]
                yBlist.append( b )

            if theX < pos[i][0] and theX > pos[j][0] :

                m = (pos[i][1] - pos[j][1]) / (pos[i][0] - pos[j][0])
                y = pos[j][1] +  m*( theX  - pos[j][0] )
                b = [ y, i, j ]
                yBlist.append( b )

            if theX > pos[i][0] and theX < pos[j][0] :
                m = (pos[j][1] - pos[i][1]) / (pos[j][0] - pos[i][0])
                y = pos[i][1] +  m*( theX  - pos[i][0] )
                b = [ y, j, i ]
                yBlist.append( b )


        #print( ' Y Boundary => y1: %.2f, y2: %.2f ' %( y1, y2) )
        ySortList = sorted( yBlist, key=itemgetter(0) )

        return ySortList


    # find intersection point from segment1 (s1,s2) and segment2(p1,p2)
    # s and p are (x,y) point
    def findIntersection(self, s1, s2, p1, p2):

        m1, d1 = SolveLine( s1[0], s1[1], s2[0], s2[1] )
        m2, d2 = SolveLine( p1[0], p1[1], p2[0], p2[1] )
        xi, yi = Intersection(m1, d1, m2, d2)
        #print( 'L1 %.2f,%.2f -  %.2f,%.2f' % ( s1[0], s1[1], s2[0], s2[1]) )
        #print( 'L2 %.2f,%.2f -  %.2f,%.2f' % ( p1[0], p1[1], p2[0], p2[1]) )
        #print( 'Sol : %.2f,%.2f ' % (xi, yi) )

        isInter = True
        if xi < min(s1[0], s2[0]) or xi > max(s1[0],s2[0] ) :
            isInter = False
        if xi < min(p1[0], p2[0]) or xi > max(p1[0],p2[0] ) :
            isInter = False
        if yi < min(s1[1], s2[1]) or yi > max(s1[1],s2[1] ) :
            isInter = False
        if yi < min(p1[1], p2[1]) or yi > max(p1[1],p2[1] ) :
            isInter = False

        return xi, yi, isInter


    # lineV is the grid chain vector
    # posV is shape outline vector
    def findBoundaryNew(self, lineV, posV, fillV ):

        xi = 0
        yi = 0
        isInter = False
        for i in range( len(lineV) -1) :

            blist12 = self.findXBoundary( lineV[i][1], posV )
            blist34 = self.findXBoundary( lineV[i+1][1], posV )
            #print(' Line X(%.1f) , boundary( %.1f ~ %.1f) ' %( lineV[i][0], b1[0], b2[0] ) )
            if len(blist12 ) != 2 :
                print(' Found XBoundary Fail 12 ! (%d) ' %(len(blist12)) )
                continue
            if len(blist34 ) != 2 :
                print(' Found XBoundary Fail 34 ! (%d) ' %(len(blist34)) )
                continue

            b1 = blist12[0]
            b2 = blist12[1]
            b3 = blist34[0]
            b4 = blist34[1]

            #if b1[0] == 0  or b2[0] == 0 :
                #print(' Line Fail !!! ')
            #    continue ;
            #if b3[0] == 0  or b4[0] == 0 :
                #print(' Line Fail !!! ')
            #    continue ;

            if lineV[i][0] > b1[0] and lineV[i][0] < b2[0] :
                fillV.append( lineV[i] )
                #print(' Accepted (%.1f, %.1f)' %( lineV[i][0], lineV[i][1]))

            if lineV[i][0] < b1[0] and lineV[i+1][0] > b3[0] :
                j = b3[1]
                k = b3[2]
                xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                if isInter is False :
                    j = b1[1]
                    k = b1[2]
                    xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )

                fillV.append( [xi,yi] )
                #print(' Found Boundary1 (%.1f, %.1f)' %(xi,yi))

            if lineV[i][0] < b2[0] and lineV[i+1][0] > b4[0] :
                j = b4[1]
                k = b4[2]
                xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                if isInter is False :
                    j = b2[1]
                    k = b2[2]
                    xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                fillV.append( [xi,yi] )
                #print(' Found Boundary2 (%.1f, %.1f)' %(xi,yi))

            if lineV[i][0] > b1[0] and lineV[i+1][0] < b3[0] :
                j = b1[1]
                k = b1[2]
                xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                if isInter is False :
                    j = b3[1]
                    k = b3[2]
                    xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                fillV.append( [xi,yi] )
                #print(' Found Boundary3 (%.1f, %.1f)' %(xi,yi))

            if lineV[i][0] > b2[0] and lineV[i+1][0] < b4[0] :
                j = b2[1]
                k = b2[2]
                xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                if isInter is False :
                    j = b4[1]
                    k = b4[2]
                    xi,yi, isInter = self.findIntersection( lineV[i], lineV[i+1], posV[j], posV[k] )
                fillV.append( [xi,yi] )
                #print(' Found Boundary4 (%.1f, %.1f)' %(xi,yi))


    # ranges : the partition range
    # boundary : the boundary of the shape
    # find the starting x0 which corresponding to the starting partition
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

    def interventionFill(self, y, ylist, dsdLnm ):

        for i in range( len(ylist) ) :

            if y == ylist[i] :
                ds = dsdLnm[i][0]
                dL = dsdLnm[i][1]
                n  = dsdLnm[i][2]
                m  = dsdLnm[i][3]
                return ds, dL, n, m


    # pos is the outline shape
    def setPatternYscale(self, scale ):

        self.yScale = scale

    def shiftPartition(self, dx, dy ):
        self.partition_dx = dx
        self.partition_dy = dy

    def FillArbitrary(self, pos, ds, dL, n, m):

        beadSpacing = self.BSScale*self.beadWidth
        poly = PolygonFill( )

        # determine the unit polygon size
        w0, h0 = poly.unitSize(ds, dL, n, m, 1. )
        h0 = (h0*self.yScale) + beadSpacing
        print('w: %.3f , h: %.3f' % (w0, h0))

        # This is the case for line-fill
        isLineFill = False
        if h0 == 0 :
            isLineFill = True
            h0 = dL

        # Find the top,bottom, left and right range
        top,bott,left,right = self.defineRange(pos)
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(top[1], bott[1], left[0], right[0]))
        # Partition the rectangle space
        nX = int( (right[0] - left[0]) / w0 ) + 1
        nY = int( (top[1]   - bott[1]) / (h0 + beadSpacing) ) + 1
        print( 'NX: %d , NY: %d' %(nX, nY) )

        # Re-define the range of partition space
        deltaX = (nX*w0) - ( right[0] - left[0] )
        #xRange = [ left[0]-(deltaX/2) + self.partition_dx , right[0]+(deltaX/2) + self.partition_dx ]
        xRange = [ left[0] + self.partition_dx , right[0]+(deltaX) + self.partition_dx ]
        deltaY = (nY*h0) - ( top[1] - bott[1] )
        #yRange = [ top[1] + (deltaY/2) + self.partition_dy , bott[1] - (deltaY/2) + self.partition_dy ]
        yRange = [ top[1] + self.partition_dy , bott[1] - deltaY + self.partition_dy ]
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(yRange[0], yRange[1], xRange[0], xRange[1]))

        # setup starting Y and X position (x0,y0)
        y0 = yRange[0] - (h0/2) + (beadSpacing/2.0) - 0.000001

        y = y0
        arcV = []
        i=0
        while y > bott[1] :

            print( '(%d) Y = %.3f ' %( i, y ) )
            lineV = []
            #xL,xR,xLs,xRs = self.findBoundary( y, dy*pow(-1,i), bott[1], top[1], pos )
            #xL,xR,xLs,xRs = self.findBoundary( y, dy*pow(-1,i), yRange[1], yRange[0], pos )

            # Assign the number of tip for upper or lower sides
            if i%4 == 0 or i%4 == 3 :
                n_tip = n
            if i%4 == 1 or i%4 == 2 :
                n_tip = m


            if i%2 == 0:
                #x = self.startX( w0, xRange, [xL,xR] )
                #poly.createLineNew( arcV, x, y, xL, xR, xLs, xRs, ds*pow(-1,i), dL, n, 1 )
                poly.createLineNew1( lineV, y, xRange, ds*pow(-1,i), dL, n_tip, self.yScale )
                self.findBoundaryNew( lineV, pos, arcV )
                y = y - beadSpacing
                if isLineFill :
                    y = y - h0
            else:
                #x = self.startX( w0, xRange, [xL,xR], True )
                poly.createLineNew1( lineV, y, xRange, ds*pow(-1,i), dL, n_tip, self.yScale )
                self.findBoundaryNew( lineV, pos, arcV )
                y = y - h0

            i = i+1


        return arcV


    # pos is the outline
    # UD : True -> From Top, False : From Bottom to top
    # LR : True -> From left to right first , False : From right to left first
    def FillSpaceY(self, pos, deltaY = 0, deltaX = 0, UD = True, LR = True  ):

        beadSpacing = (self.BSScale*self.beadWidth)
        stepY = beadSpacing + deltaY
        xGap = beadSpacing + deltaX

        # Find the top,bottom, left and right range
        top,bott,left,right = self.defineRange(pos)
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(top[1], bott[1], left[0], right[0]))

        # setup beadspacing
        dw = ( top[1] - bott[1] ) % stepY
        n = (( top[1] - bott[1] ) / stepY) - 1
        stepY = stepY + (dw/n)

        # setup the starting Y position
        y0 = top[1] - stepY
        if UD is False :
            y0 = bott[1] + stepY
            stepY = -1*stepY

        y = y0
        fillV = []
        for i in range( int(n) ) :

            xblist = self.findXBoundary( y , pos )
            b1 = xblist[0]
            b2 = xblist[1]
            if i%2 == 0:
                if LR is True :
                    fillV.append( [ b1[0] + xGap , y ] )
                    fillV.append( [ b2[0] - xGap, y ] )
                else :
                    fillV.append( [ b2[0] - xGap, y ] )
                    fillV.append( [ b1[0] + xGap, y ] )

            else :
                if LR is True :
                    fillV.append( [ b2[0] - xGap, y ] )
                    fillV.append( [ b1[0] + xGap, y ] )
                else :
                    fillV.append( [ b1[0] + xGap , y ] )
                    fillV.append( [ b2[0] - xGap, y ] )


            y = y - stepY

        return fillV

    # Fill a space with vertical line ( x = k ~ X = k+n )
    # LR : True -> From left , False : From right
    # UD : True -> From Top to bottom first, False : From Bottom to top first
    def FillSpaceX(self, pos,  deltaX = 0, deltaY = 0, LR = True , UD = False ):

        # Setup each x step
        beadSpacing = (self.BSScale*self.beadWidth)
        stepX = beadSpacing + deltaX
        yGap = beadSpacing + deltaY

        # Find the top,bottom, left and right boundary
        top,bott,left,right = self.defineRange(pos)
        print( 'Range top: %.2f , bott: %.2f, left: %.2f , right: %.2f' %(top[1], bott[1], left[0], right[0]))

        # setup beadspacing - fine tune to evenly cover the whole X space
        dw = ( right[0] - left[0] ) % stepX
        n = (( right[0] - left[0] ) / stepX) - 1
        stepX = stepX + (dw/n)

        # start filling - one x step from the outline
        x0 = left[0] + stepX
        if LR is False :
            x0 = right[0] - stepX
            stepX = -1*stepX

        x = x0
        fillV = []
        for i in range( int(n) ) :

            # finding the y boundary and the corresponding outline segment
            # the list is sorted from small y value to large y value
            yblist = self.findYBoundary( x , pos )

            if i%2 == 0 :
                if UD is True :
                    fillV.append( [x, yblist[1][0] + (-1*yGap) ] )
                    fillV.append( [x, yblist[0][0] + (yGap) ] )
                if UD is False :
                    fillV.append( [x, yblist[0][0] + (yGap) ] )
                    fillV.append( [x, yblist[1][0] + (-1*yGap) ] )
            else :
                if UD is True :
                    fillV.append( [x, yblist[0][0] + (yGap) ] )
                    fillV.append( [x, yblist[1][0] + (-1*yGap) ] )
                if UD is False :
                    fillV.append( [x, yblist[1][0] + (-1*yGap) ] )
                    fillV.append( [x, yblist[0][0] + (yGap) ] )


            '''
            if i%2 == 0:

                # go through all y boundaries
                for j in range( len(yblist) ) :
                    p = 1
                    if j%2 == 1 :
                        p = -1
                    fillV.append( [x, yblist[j][0] + (p*yGap) ] )
            else :
                for j in range( len(yblist) ) :
                    k = len(yblist) -1 - j
                    p = -1
                    if k%2 == 0 :
                        p = 1
                    fillV.append( [x, yblist[k][0] + (p*yGap) ] )
            '''
            x = x + stepX

        return fillV
