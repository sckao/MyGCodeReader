import math
import numpy as np
from ReadRecipe import ReadRecipe

# Solve slope (m) and intercept(d) given two points (x1, y1) , (x2, y2)
#    y = mx + d
#  |y1| = | x1  1 | | m |
#  |y2|   | x2  1 | | d |
#   a = np.array([x1, 1] , [x2,1])   b = [y1, y2] , c = [m,d]
def SolveLine( x1, y1, x2, y2 ) :
    # to avoid m is infinit
    if x1 == x2 :
        x2 = x2*0.999999
    a = np.array( [[ x1, 1.] , [ x2, 1.]]  )
    b = np.array( [y1, y2 ]  )
    c = np.linalg.solve(a,b)
    m = c[0]
    d = c[1]

    return m,d

# Solve two line ( y = mx + d )
# return intersection point x,y
def Intersection( m1, d1, m2, d2 ) :
    if m1 == m2 :
        m1 = m1*1.0000001
        m2 = m2*0.9999999
    a = np.array( [[m1, -1.], [m2, -1.]] )
    b = np.array( [ -1*d1, -1*d2 ] )
    c = np.linalg.solve(a, b)
    x = c[0]
    y = c[1]
    return x,y
    # print( '(%d,%d) = [ %.3f, %.3f ]' %( i, j, c[0], c[1]) )

class PolygonFill:

    # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh)
    bh = 0.5
    ts = 0.35
    fh = 0.1

    # Linear density ( or Flow rate )
    rho = 0.75
    Fval = 6000.
    Eval = Fval*rho


    def __init__( self, bw = 1.75 ):

        # n must be >=  3
        self.pos = []
        self.beadwidth = bw
        self.u = []
        self.v = []
        self.z = []
        self.s = []
        self.ads = 0
        self.rth = 5
        self.rEval = -1

    def setParameters(self, fval_new = 6000 , rho_new = 0.75, bw_new = 0.75 ):

        self.Fval = fval_new
        self.rho = rho_new
        self.beadwidth = bw_new
        self.Eval = self.Fval*self.rho

    def setTipHeight(self, ts0 = 0.35 , bh0 = 0.5, fh0 = 0.1):

        # Tip speace (ts) and Bead height (bh) and first layer adjustment (fh)
        self.ts = ts0
        self.bh = bh0
        self.fh = fh0

        self.z0 = self.ts + self.bh + self.fh
        return self.z0

    def setRetraction(self, rth, rEval):
        self.rth = rth
        self.rEval = rEval

    # setup the spacing between upper and lower arc. The default is 1 beadwidth
    # the scale is the addition adjustment
    # adjustment = arc_spacing_scale* beadwidth
    def setArcSpacing(self, arc_spacing_scale = 0  ):
        self.ads = arc_spacing_scale


    def reset(self):

        self.u = []
        self.v = []
        self.z = []
        self.s = []

    def getResult(self, pos= [], xlist=[], ylist=[], z_input =0, status =1 ):

        for i in range( len(pos)) :

            xlist.append( pos[i][0] )
            ylist.append( pos[i][1] )
            self.u.append( pos[i][0] )
            self.v.append( pos[i][1] )
            self.z.append( z_input )
            self.s.append( status )


    def getData4Gcode(self, rx=[], ry=[], rz=[],rs=[], rE=[], retract = False ):

        eVal = 0
        for i in range(len(self.s)) :

            if i == 0:
                eVal = -1.

                # Adding retraction
                if len(rx) > 0 and retract :
                    print("Retract !")
                    rx.append( rx[ -1 ] )
                    ry.append( ry[ -1 ] )
                    rz.append( rz[ -1 ] + self.rth )
                    rE.append( self.rEval )
                    rs.append( 2 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(rz[-1]  )
                    rE.append( 0 )
                    rs.append( 0 )
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(self.z[i] )
                    rE.append( 0.1 )
                    rs.append( -2 )
                else :
                    print("Fresh Start !")
                    rx.append(self.u[i])
                    ry.append(self.v[i])
                    rz.append(self.z[i] )
                    rE.append( 0.0 )
                    rs.append( 0 )

            else :
                dx = self.u[i] - self.u[i-1]
                dy = self.v[i] - self.v[i-1]
                dl = math.sqrt( (dx*dx) + (dy*dy) )
                dt = dl / self.Fval
                eVal = self.Eval * dt
                if self.s[i] != 1 :
                    eVal = 0

                rx.append(self.u[i])
                ry.append(self.v[i])
                rz.append(self.z[i] )
                rE.append( eVal )
                rs.append(self.s[i] )


    # Create upper or lower part of the polygon chains
    # ds < 0 is for the lower part
    # scale is for scaling y position
    # pos is the return arc position
    def createArc(self, xc, yc, ds, n, pos, scale = 1.):

        theta = math.pi / (n+1)
        r = abs(ds/2.)

        # Only add the initial point if this is the starting point
        #if len(pos) < 1 :
        #    pos.append( [x0,y0] )

        j = n
        max_dy = 0
        # This part only fill intermediate points
        k = 1
        for i in range(n) :

            # upper part of arc
            if ds > 0 :
                j = n - i
            # bottom part of arc
            if ds < 0 :
                j = -1*(i+1)
            dx = r*math.cos( theta*j )
            dy = r*math.sin( theta*j )*scale

            if abs(dy) > max_dy :
                max_dy = abs(dy)

            x = xc + dx
            y = yc + dy
            #print('   (j=%d) , theta = %.3f, x=%.3f y= %.3f' %(j, theta*j, x, y))
            pos.append( [x,y] )

        return max_dy

    # Create upper or lower part of the polygon chains
    # ds < 0 is for the lower part
    # scale is for scaling y position
    # pos is the return arc position
    # points outside boundary (iniB, endB) will not be added
    def createArcNew(self, xc, yc, iniB, endB, ds, n, pos, scale = 1.):

        theta = math.pi / (n+1)
        r = abs(ds/2.)

        j = n
        max_dy = 0
        # This part only fill intermediate points
        k = 1

        for i in range(n) :

            # upper part of arc
            if ds > 0 :
                j = n - i
            # bottom part of arc
            if ds < 0 :
                j = -1*(i+1)
            dx = r*math.cos( theta*j )
            dy = r*math.sin( theta*j )*scale

            if abs(dy) > max_dy :
                max_dy = abs(dy)

            x = xc + dx
            y = yc + dy
            #print('   (j=%d) , theta = %.3f, x=%.3f y= %.3f' %(j, theta*j, x, y))
            if x < max(iniB,endB) and x > min(iniB,endB) :
                pos.append( [x,y] )
                #print( ' x = %.2f ' %(x) )

            '''    
            if x < min(iniB,endB) and i < n-1 :
                x = min(iniB,endB)
                if len(pos) < 1 :
                    pos.append( [x,y] )
                    print( ' x = %.2f @ %d) ' %(x,i) )
                elif pos[-1][0] != x or pos[-1][1] != y :
                    pos.append( [x,y] )
                    print( ' x = %.2f @ %d) ' %(x,i) )
            if x > max(iniB,endB) and i < n-1 :
                x = max(iniB,endB)
                if pos[-1][0] != x or pos[-1][1] != y :
                    pos.append( [x,y] )
                    print( ' x = %.2f @ %d) ' %(x,i) )
            '''


        return max_dy


    # k is number of bead (wallthickness, not height) for the polygon
    # x0,y0 :  starting position
    # Lx : length of the polygon chain
    # ds : diameter of the polygon, dL : spacing between polygons
    # n,m : number of points in upper or lower arch
    # scale : scale the height of the (half) polygon
    def createChain(self,x0,y0, Lx, ds, dL, n, m, k = 1, scale = 1. ):

        # Setup parameters
        i = 1
        arcs = []
        d = self.beadwidth
        angle1 = math.pi/((n+1)*2)
        angle2 = math.pi/((m+1)*2)
        cor =  (d/math.cos(angle1)) - (d*math.tan(angle1))
        h1 = 0

        # start routing
        # adding the first segment
        x = x0
        y = y0 + ((k-1)*d)
        arcs.append([x,y])
        x = x0 + dL - ((k-1)*cor)
        y = y0 + ((k-1)*d)
        arcs.append([x,y])

        # used for constructing arc
        xc = x0 + dL + (ds/2)
        yc = y0
        while  Lx >= (ds+dL)*i :

            # radius to construct the polygon
            r = ds + ((k-1)*d*2/math.cos(angle1))

            #print(" (%d) xc,yc,r =  %.3f, %.3f , %.3f" %(i, xc,yc, r))
            h1 = self.createArc( xc, yc, r, n, arcs, scale )
            if (ds+dL)*(i+1) <= Lx :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                x = arcs[-1][0] + dL - ((k-1)*cor*2)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
            else :
                x = x0 + (dL+ds)*i + ((k-1)*cor)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )
                x = arcs[-1][0] + dL - ((k-1)*cor) + ((k-1)*d)
                y = y0 + ((k-1)*d)
                arcs.append( [x, y] )

            xc = xc + dL + ds
            i = i+1

        # Setup manual adjustment y position
        ad = self.ads*d

        # shift downward
        y = y - (d*(2*k-1)) + ad
        arcs.append( [x, y])
        x = arcs[-1][0] - dL +  ((k-1)*cor) - ((k-1)*d)
        arcs.append( [x, y])

        # used for constructing arc
        yc = yc - d + ad
        xc = xc - dL - ds
        i = i-1
        h2 = 0
        j = 1
        cor =  (d/math.cos(angle2)) - (d*math.tan(angle2))
        #print(" >> xc,yc = %.3f, %.3f " %(xc,yc))
        while i > 0 :


            r = -1*ds - ((k-1)*d*2/math.cos(angle2))
            #print(" (%d) xc,yc,r =  %.3f, %.3f , %.3f" %(i, xc,yc, r))
            h2 = self.createArc( xc,yc, r, m, arcs, scale )
            if i > 1 :
                x = x - ds - ((k-1)*cor*2)
                y = y0 -d - ((k-1)*d) + ad
                arcs.append( [x, y] )

                x = x - dL + ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d) + ad
                arcs.append( [x, y] )
            else :
                x = x  - ds - ((k-1)*cor*2)
                y = y0 - d - ((k-1)*d) + ad
                arcs.append( [x, y] )

            xc = xc - dL - ds
            i = i-1
            j = j+1

        x = x -dL + ((k-1)*cor)
        y = y
        arcs.append([x,y])
        #print( ' ** End at  xy = (%.3f , %.3f)' %( x, y))
        h = h1+h2
        return arcs, h

    # Generate a general polygon, could be a partial polygon
    def createPolygon(self, nside, iniPos, endPos, xc, yc ):

        # Getting initial radius ri and ending radius rj
        # Initial/ending angle in the range of 0 ~ 2pi
        ri = math.sqrt( ((xc - iniPos[0] )*(xc-iniPos[0])) + ((yc - iniPos[1] )*(yc-iniPos[1])) )
        rj = math.sqrt( ((xc - endPos[0] )*(xc-endPos[0])) + ((yc - endPos[1] )*(yc-endPos[1])) )
        iniA = math.acos( (iniPos[0]-xc )/ri )
        endA = math.acos( (endPos[0]-xc )/rj )
        if iniPos[1] < yc :
            iniA = (math.pi*2) - iniA
        if endPos[1] < yc :
            endA = (math.pi*2) - endA


        R = ri
        #dR = (rj - ri) / nside
        dR = 0
        dPhi = 0
        arcV = []
        if endA > iniA :
            dPhi = (endA - iniA) / nside
        else :
            dPhi =  (2*math.pi - (iniA - endA )) / nside

        for i in range( nside ) :
            Phi = iniA + (i*dPhi)
            x = R*math.cos( Phi ) + xc
            y = R*math.sin( Phi ) + yc
            arcV.append( [x,y] )
            R = R + dR

        return arcV

    def unitSize(self, ds, dL, n, m, k = 1, scale = 1.):
        arcs, h = self.createChain( 0, 0,dL+ds, ds, dL, n, m, k, scale )
        width = ds + dL
        #height = h + self.beadwidth
        height = h
        return width, height

    # iniP and endP are the boundary position
    # startp is the starting position, it must be between iniP and endP
    # yScale is to stretch the length
    # ds < 0 means opposite direction (from right to left)
    def createLine(self, arcV , iniP, endP, startP, ds, dL, n, yScale = 1 ):

        pathL = abs( endP[0] - iniP[0] )
        # get the direction
        pn = 1
        if ds < 0 :
            pn = -1

        x = iniP[0]
        y = iniP[1]
        arcV.append( [x, y] )

        x = startP[0]
        y = startP[1]
        arcV.append( [x, y] )

        dX  = abs(startP[0] - iniP[0])
        i = 0
        while dX < pathL :

            #print('(%d) dX = %.3f ' %(i, dX))
            # creating polygon
            xc = x + (ds/2)
            yc = y
            self.createArc( xc, yc, ds, n, arcV, yScale )

            x = x + ds
            arcV.append( [x,y] )
            dX = dX + abs(ds)

            if ( dX + dL ) < pathL :
                x = x + (dL*pn)
                arcV.append( [x,y] )
                dX = dX + dL
                # if the rest of length is not long enough to get an arc and a connecting segment, stop
                if ( dX + abs(ds) + dL ) > pathL :
                    x = endP[0]
                    y = endP[1]
                    arcV.append([x,y])
                    dX = pathL
                    #print(' finished 1 -  [%.3f , %.3f ]' %(x,y))
            else :
                x = endP[0]
                y = endP[1]
                arcV.append([x,y])
                dX = pathL
                #print(' finished 2 - [%.3f , %.3f ]' %(x,y) )

            i = i+1

    # iniP and endP are the boundary for the main line
    # iniPs and endPs are the boundary for the arc points
    # theX is the starting position from the partition
    def createLineNew(self, arcV , theX, theY,  iniP, endP, iniPs, endPs, ds, dL, n, yScale = 1 ):

        pathL = abs( endP - iniP )
        # get the direction
        pn = 1
        if ds < 0 :
            pn = -1

        # Add the 1st/starting point
        x = theX
        y = theY

        dX = 0
        while dX < pathL :

            #print('(%d) dX = %.3f ' %(i, dX))
            # 0. For reversed direction, dL first then ds
            if ds < 0 and dX == 0 :
              x = x + (dL*pn)
              if x > min(iniP, endP) and x < max(iniP,endP) :
                  arcV.append( [x,y] )
                  dX = abs(x - iniP)

            # 1. Creating polygon - the middle points, not include the start and the end points
            xc = x + (ds/2)
            yc = y
            self.createArcNew( xc, yc, iniPs, endPs, ds, n, arcV, yScale )

            if dX + abs(ds) > pathL :
                x = endP
                arcV.append([x,y])
                dX = pathL
            else :
                x = x + ds
                if x > min(iniP, endP) and x < max(iniP,endP) :
                    arcV.append( [x, y] )
                else :
                    # x value can NOT be changed in this case, otherwise the grid will off-phase
                    if ds > 0 :
                        arcV.append( [ min(iniP, endP), y] )
                    if ds < 0 :
                        arcV.append( [ max(iniP, endP), y] )

                dX = abs(x - iniP)
                print( ' x1 = %.2f , dX = %.2f / %.2f' %(x, dX, pathL) )

            # 2. Add connecting segment
            if ( dX + dL ) < pathL :
                x = x + (dL*pn)
                arcV.append( [x,y] )
                dX = abs(x - iniP)
                print( ' x2 = %.2f , dX = %.2f / %.2f' %(x, dX, pathL) )
            else :
                x = endP
                arcV.append([x,y])
                dX = pathL
                #print(' finished 2 - [%.3f , %.3f ]' %(x,y) )


    # pRange is the X range of the partition
    def createLineNew1(self, arcV , theY, pRange, ds, dL, n, yScale = 1 ):

        pn = 1
        if ds < 0 :
            pn = -1

        # partition X range
        iniX = pRange[0]
        endX = pRange[1]
        if pn < 0 :
            iniX = pRange[1]
            endX = pRange[0]

        pathL = abs( endX - iniX )
        # get the direction
        # buffer line result - will be checked with boundaries
        lineV = []
        # Add the 1st/starting point
        x = iniX
        y = theY
        lineV.append( [x,y] )

        dX = 0
        dY = 0
        # Layout grid through the whole partition space
        while dX < pathL :

            #print('(%d) dX = %.3f ' %(i, dX))
            # 0. For reversed direction, dL first then ds
            if ds < 0 and dX == 0 :
                x = x + (dL*pn)
                lineV.append( [x,y] )
                dX = abs(x - iniX)

            # 1. Creating polygon - the middle points, not include the start and the end points
            xc = x + (ds/2)
            yc = y
            dY = self.createArcNew( xc, yc, iniX, endX, ds, n, lineV, yScale )

            if dX + abs(ds) > pathL :
                x = endX
                lineV.append([x,y])
                dX = pathL
            else :
                x = x + ds
                lineV.append( [x, y] )
                dX = abs(x - iniX)
                #print( ' x1 = %.2f , dX = %.2f / %.2f' %(x, dX, pathL) )

            # 2. Add connecting segment
            if ( dX + dL ) < pathL :
                x = x + (dL*pn)
                lineV.append( [x,y] )
                dX = abs(x - iniX)
                #print( ' x2 = %.2f , dX = %.2f / %.2f' %(x, dX, pathL) )
            else :
                x = endX
                lineV.append([x,y])
                dX = pathL
                #print(' finished 2 - [%.3f , %.3f ]' %(x,y) )

        dY = dY*pn
        # review points and strips those out of boundary
        nPnt = len(lineV)
        #print(' N Point = %d , dY = %.2f' %(nPnt, dY) )
        for i in range( nPnt ) :
            arcV.append( lineV[i] )


    # Input starting x,y positions and length (L)
    def FillAreaN(self, xV, yV, LV, ds, dL, n, m, k = 1, z = 0, scale = 1. ):

        iniX = xV[0]
        iniY = yV[0]
        x = []
        y = []
        for j in range(k) :

            j = j+1
            for i in range( len(LV) ) :
                print(' Printing Row %d' %(i))
                y_start = yV[i] + (j-1)*self.beadwidth
                # Move to next row
                if xV[i] > iniX :
                    arc = []
                    arc.append( [ iniX, y_start ])
                    arc.append( [ xV[i], y_start ])
                    self.getResult( arc, x,y, z, 0)
                elif xV[i] < iniX :
                    arc = []
                    iniY = y[-1]
                    arc.append( [ xV[i], iniY])
                    arc.append( [ xV[i], yV[i]])
                    self.getResult( arc, x,y, z, 0)
                else :
                    arc = []
                    arc.append( [ xV[i], yV[i]])
                    self.getResult( arc, x,y, z, 1)


                #arc = []
                #arc.append( [ xV[i], yV[i]])
                #self.getResult( arc, x,y, z, 0)

                # Move to starting point of this row
                iniX = xV[i]
                iniY = yV[i]
                if i%2 == 0 :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, n, m, j, scale)
                    self.getResult( arcs, x,y, z, 1)
                else :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, m, n, j, scale)
                    self.getResult( arcs, x,y, z, 1)

        return x, y

    # Input starting x,y positions and length (L)
    # xV, yV : starting positions, LV: length of the chain
    # fV : left side connecting points between rows
    def FillArea(self, xV, yV, LV, fV, ds, dL, n, m, k = 1, z = 0, scale = 1. ):

        iniX = xV[0]
        iniY = yV[0]
        x = []
        y = []
        for j in range(k) :

            j = j+1
            for i in range( len(LV) ) :
                print(' Printing Row %d' %(i))

                # Move to starting point of this row
                iniX = xV[i]
                iniY = yV[i]
                if i%2 == 0 :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, n, m, j, scale)
                    self.getResult( arcs, x,y, z, 1)
                else :
                    arcs, h = self.createChain( iniX, iniY, LV[i],ds, dL, m, n, j, scale)
                    self.getResult( arcs, x,y, z, 1)

                self.getResult(fV[i], x,y,z, 1 )



        return x, y

    def addSkirt(self, x0, y0, LV, ds, dL, n, m, k, delta = 5, scale = 1 ):

        w0 , h0 = self.unitSize(ds,dL,n, m, k, scale )
        print( 'Unit size = %.3f , %.3f' %(w0, h0))

        width = max(LV)
        height = len(LV)*h0
        print( ' Pattern height = %.3f ' %(height) )

        # Just reset internal containers for x,y,z and s
        self.reset()

        # point 1
        x = x0 - delta
        y = y0 + delta + (h0/2)
        self.u.append( x )
        self.v.append( y )
        self.z.append( self.z0 )
        self.s.append( 1 )

        # point2
        x = x + width + (2*delta) + dL
        y = y
        self.u.append( x )
        self.v.append( y )
        self.z.append( self.z0 )
        self.s.append( 1 )

        # point3
        x = x
        y = y - height - (2*delta)
        self.u.append( x )
        self.v.append( y )
        self.z.append( self.z0 )
        self.s.append( 1 )

        # point4
        x = x - width - (2*delta) - dL
        y = y
        self.u.append( x )
        self.v.append( y )
        self.z.append( self.z0 )
        self.s.append( 1 )

        # back to point1
        x = x
        y = y + height + (2*delta)
        self.u.append( x )
        self.v.append( y )
        self.z.append( self.z0 )
        self.s.append( 1 )

    # Not complete yet
    def partition(self, shell, ds, dL, n, m ):

        # Find the min x,y and max x,y
        max_x = -9999.
        max_y = -9999.
        min_x = 9999.
        min_y = 9999.
        for i in range( len(shell)) :

            x = shell[i][0]
            y = shell[i][0]
            if x > max_x :
                max_x = x
            if x < min_x :
                min_x = x
            if y > max_y :
                max_y = y
            if y < min_y :
                min_y = y

        wShell = max_x - min_x
        hShell = max_y - min_y

        # Find the unit width(w0) and height(h0)
        w0 , h0 = self.unitSize( ds, dL, n, m)

        #
        nw = int(wShell/w0)
        nh = int(hShell/h0)

