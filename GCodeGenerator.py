import math

# Return cos ( 0 ~ pi )
def dTheta( x1, y1, x2, y2, x3, y3 ) :

    a = [x2-x1, y2-y1, 0.]
    b = [x3-x2, y3-y2, 0.]
    ab  = (a[0]*b[0]) + ( a[1]*b[1] )
    al = math.sqrt( (a[0]*a[0]) + (a[1]*a[1])  )
    bl = math.sqrt( (b[0]*b[0]) + (b[1]*b[1])  )

    if al > 0. and bl > 0. :
        cosA = ab/(al*bl)
    else :
        cosA = -9
    #print(" ab: %.3f , al: %.3f  , bl: %.3f cos =  %.4f" %(ab, al, bl, cosA) )
    return cosA
    #angle = math.acos( cosA*0.999 )
    #print( ' cosA = %.3f , A = %.3f - %.3f' %(cosA, angle, angle*180/3.1415926 ) )

    return angle

def dLength(x1, y1, x2, y2) :

    dx = x2 - x1
    dy = y2 - y1
    dL = math.sqrt( (dx*dx) + (dy*dy) )
    return dL


# Ratio is percentage of the breaking point from (x2, y2)
# segment is from (x1,y1) to (x2,y2)
def BreakSegment( x1,y1, x2,y2, ratio ):

    dx = x2 -x1
    dy = y2 -y1
    x0 =  x2 - dx*ratio
    y0 =  y2 - dy*ratio
    return [x0,y0]

# rs status = 9 for ending
# For a printing section, slow down in the end ( in the final "flength" )
def Ending( flength, rs = [], rx = [], ry = [], rz = [], rE = [] ):

    endingScale = 0.5
    j = len( rs ) - 1
    print(" Ending section (%d) " %(j) )
    for i in range( len(rs) ) :

        L = dLength( rx[j], ry[j], rx[j-1], ry[j-1] )
        dz = rz[j] - rz[j-1]
        if L == 0 and dz > 0 :
            print('1. this is retraction ')
            j = j -1
            continue

        if L > flength :
            print('2. Break ')
            bp = BreakSegment( rx[j-1], ry[j-1], rx[j], ry[j], flength/L )
            ## re-calculate the E Value for the 1st segment
            dL = dLength(rx[j-1], ry[j-1], bp[0], bp[1] )
            eVal0 = rE[j] * dL / L

            rx.insert(j, bp[0])
            ry.insert(j, bp[1])
            rz.insert(j, rz[j])
            rE.insert(j, eVal0)
            rs.insert(j, 1)
            print(' == > ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' %( rx[j-1], ry[j-1], rx[j], ry[j], eVal0, rs[j]))
            ## re-calculate the E Value for the 2nd segment
            ## Only use
            dL = dLength(rx[j+1], ry[j+1], bp[0], bp[1] )
            eVal1 = endingScale*rE[j] * dL / L
            rE[j+1] = eVal1
            rs[j+1] = 9
            print(' ===> ( %.3f, %.3f) -> ( %.3f, %.3f) ' %( rx[j + 1], ry[j + 1], rx[j], ry[j]))
            break
        else :
            print('3. Slow down ')
            rE[j] = endingScale*rE[j]
            rs[j] = 9

        j = j -1


# Generate GCode based on given x,y,z position and extrusion E , status (retract or move or print)
# Basic Functions : initTool, Generate, EndingGCode
# Support Functions : setMixingRatio, shift, tipWipe,
#
class GCodeGenerator :

    # Linear density ( or Flow rate )
    rho = 0.6
    Fval = 2000.
    Eval = Fval*rho


    def __init__(self, rs = [], rx =[], ry=[], rz=[], rE=[], F =2000, rho = 0.6 ):

        self.rs = rs
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.rE = rE
        self.F   = F
        self.rho = rho
        self.Eval = F*rho
        self.gF1 = F
        self.gF2 = F

        self.sx = 0
        self.sy = 0
        self.sz = 0
        self.sE = 1
        self.sF = 1
        self.ratioA = 5000
        self.ratioB = 5000
        self.angle0 = 1.57

        # Open a text file
        gfilename = input('Generated GCode filename : ')
        if gfilename == '':
            gfilename = 'gout.gcode'
        self.gfile = open( gfilename , 'w')


    def Shift(self, sx0 = 0., sy0 = 0. , sz0 = 0., sE0 = 1., sF0 = 1. ):

        self.sx = sx0
        self.sy = sy0
        self.sz = sz0
        self.sE = sE0
        self.sF = sF0

    def SetGlideSpeed(self, F1 , F2 ):
        self.gF1 = F1
        self.gF2 = F2

    # Mixing ratio is defined as A/B
    def setMixingRatio(self, ratio = 1 ):

        rb = int ( 10000/(ratio + 1) )
        ra = int ( 10000 - rb )
        self.ratioB = rb
        self.ratioA = ra

    def Retract(self, up = 2, down = 2, rS = [], rx = [], ry = [], rz = [], rE = []  ):

             i = len( rx ) -1
             rx.append( rx[i] )
             ry.append( ry[i] )
             rz.append( rz[i]+ up  )
             rE.append( -1  )
             rS.append( 2 )



    # Perform gliding
    def Gliding(self, gTime1, eRatio1 , gTime2, eRatio2, rS = [], rx = [], ry = [], rz = [], rE = [] ):

        # gd: Gliding distance (mm) : Def by  x sec in whatever speed ( mm/sec )
        gd1 = gTime1 * self.gF1 / 60.
        gd2 = gTime2 * self.gF2 / 60.
        print(' Start Gliding rS size = %d -> %.3f , %.3f' % (len(rS), gd1, gd2))

        doGlide = False
        i = 0
        for it in rS:

            print(' SIZE = %d' % (len(rS)))

            # No gliding for retraction
            if it == 0 or abs(it) == 2:
                i = i + 1
                continue
            #
            if len(rE) > 3 and i < (len(rE) - 3):
                print('     ( %.3f, %.3f) -> ( %.3f, %.3f) -> ( %.3f, %.3f)' % (
                rx[i], ry[i], rx[i + 1], ry[i + 1], rx[i + 2], ry[i + 2]))


            # Cannot do the gliding since there are less than 3 points
            if i > len(rE) - 3:
                doGlide = False
                break

            # Check the angle to see if gliding is necessary
            angle = dTheta(rx[i], ry[i], rx[i + 1], ry[i + 1], rx[i + 2], ry[i + 2])
            print(' (%d) = angle = %.3f ' % (i, angle))
            # if abs(angle) > 1.57 and rE[i] >= 0 :
            if angle <= 0. and angle > -1. and rE[i] >= 0:
                doGlide = True

            if doGlide:
                print(' **** Gliding !! ')
                # Calculate the segment length
                L1 = dLength(rx[i], ry[i], rx[i + 1], ry[i + 1])
                L2 = dLength(rx[i + 1], ry[i + 1], rx[i + 2], ry[i + 2])

                # Break the segment
                # adding another point
                j = i+1
                k = i+2
                if  gd1 < L1  :

                    # Set gliding position
                    ratio = gd1 / L1
                    bp = BreakSegment(rx[i], ry[i], rx[i+1], ry[i+1],ratio)

                    ## re-calculate the E Value for the 1st segment
                    dL = dLength(rx[i], ry[i], bp[0], bp[1] )
                    eVal0 = self.Eval * dL / self.F
                    rx.insert(i + 1, bp[0])
                    ry.insert(i + 1, bp[1])
                    rz.insert(i + 1, rz[i])
                    rE.insert(i + 1, eVal0)
                    rS.insert(i + 1, 1)
                    print(' == > ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' %( rx[i], ry[i], rx[i + 1], ry[i + 1], eVal0, rS[i + 1]))
                    ## re-calculate the E Value for the 2nd segment
                    dL = dLength(rx[i + 2], ry[i + 2], bp[0], bp[1] )
                    scale = self.gF1 / self.F
                    eVal1 = self.Eval * dL * eRatio1 * scale / self.gF1
                    rE[i + 2] = eVal1
                    rS[i + 2] = 3
                    print(' ===> ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' %( rx[i + 1], ry[i + 1], rx[i + 2], ry[i + 2], eVal1, rS[i + 2]))
                    j = j+1
                    k = k+1
                else :
                    dL = dLength(rx[i + 1], ry[i + 1], rx[i], ry[i])
                    scale = self.gF1 / self.F
                    eVal1 = self.Eval * dL * eRatio1 * scale / self.gF1
                    rE[i+1] = eVal1
                    rS[i+1] = 3


                # Turnning point
                if gd2 < L2 :
                    # Set gliding position
                    ratio = abs(L2 - gd2) / L2
                    bp = BreakSegment(rx[j], ry[j], rx[j+1], ry[j+1],ratio)

                    ## re-calculate the E Value for the 1st segment
                    dL = dLength(bp[0], bp[1], rx[j], ry[j])
                    scale = self.gF2 / self.F
                    eVal2 = self.Eval * dL * eRatio2 * scale / self.gF2
                    rx.insert( j+1 , bp[0])
                    ry.insert( j+1 , bp[1])
                    rz.insert( j+1 , rz[i])
                    rE.insert( j+1 , eVal2)
                    rS.insert( j+1 , 4)
                    print(' ---> ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' % ( rx[j+1], ry[j+1], rx[j+1], ry[j+1], eVal2, rS[j+1] ))

                    ## re-calculate the E Value for the 2st segment
                    dL = dLength(bp[0], bp[1], rx[j+2], ry[j+2])
                    eVal0 = self.Eval * dL / self.F
                    rE[j+2] = eVal0
                    print(' -- > ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' % ( rx[j+2], ry[j+2], rx[j+2], ry[j+2], eVal0, rS[j+2]))
                    k = k+1
                else :
                    dL = dLength(rx[j + 1], ry[j + 1], rx[j], ry[j])
                    scale = self.gF2 / self.F
                    eVal2 = self.Eval * dL * eRatio1 * scale / self.gF2
                    rE[j+1] = eVal2
                    rS[j+1] = 4

                doGlide = False
                i = k -1
            else:
                print(' ==== Pass !! ')
                i = i + 1

        print(' Gliding done !')

    # set mixing ratio
    def setIndex(self):
        self.gfile.write('; Set up mixing ratio \n')
        self.gfile.write('M163 S0 P%d                    ; Set extruder mix ratio B\n' %(self.ratioB))
        self.gfile.write('M163 S1 P%d                    ; Set extruder mix ratio A\n' %(self.ratioA))
        self.gfile.write('M163 S2 P0                     ; Enable Extruder \n')
        self.gfile.write('M83                            ; Relative extrusion mode\n')

    # At least 30 sec for each pause.
    # X limit is 360
    def tipWipe(self, pauseTime = 60.0, nextX = 0, nextY = 0 ):

        # Center of the drain cup
        x0 = 345
        y0 = 10
        # Distance between cup center to brush left edge
        Lcb = 36
        # Brush Length
        Lbrush = 35
        # wiping range (between xL and xR)
        xL = x0 - Lcb
        xR = xL - Lbrush
        # Purge E value
        purgeE = 80
        # Purge distance
        dX = 15
        dY = 10

        # number of pause/drain cycle
        n = int ( pauseTime / 30)
        residualTime = pauseTime%30
        if residualTime > 0 and n > 0 :
            n = n + 1

        self.gfile.write('; Pause and Flush tip \n')
        self.gfile.write('G0 Z35.500 F8000 \n')
        self.gfile.write('G0 Y%.3f F8000 \n' %(y0) )
        self.gfile.write('G0 X%.3f F8000 \n' %(x0) )
        self.gfile.write('G4 S1.0                 ; Pause for (time) seconds \n')
        self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 + dX), y0, purgeE) )
        self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 - dX), y0, purgeE) )
        self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 + dX), y0, purgeE) )

        y = y0
        for i in range(n) :

            self.gfile.write('G4 S30.0                 ; Pause for (time) seconds \n')
            y = y + dY
            self.gfile.write('G0 Y%.3f F8000 \n' %(y) )
            self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 - dX), y, purgeE) )
            self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 + dX), y, purgeE) )
            y = y - (2*dY)
            self.gfile.write('G0 Y%.3f F8000 \n' %(y) )
            self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 - dX), y, purgeE) )
            self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( (x0 + dX), y, purgeE) )
            y = y0
            self.gfile.write('G0 Y%.3f F8000 \n' %(y) )

            ds = 3
            if i%2 == 1 :
                ds = -3
            y = y + ds

        if residualTime > 0 :
            self.gfile.write('G4 S%.0f \n' %(residualTime) )
            self.gfile.write('G1 X%.3f Y%.3f E%.3f F8000 \n' %( x0, y0, purgeE) )

        self.gfile.write('G4 S3.0 \n')

        # Manual wipe position
        #self.gfile.write('G0 X%.3f Y280.000 F8000 \n' %(x0))
        #self.gfile.write('G0 X50.000 Y280.000 F8000 \n' )
        #self.gfile.write('G4 S3.0 \n')

        # Tip wipe position
        self.gfile.write('G0 X%.3f Y6.000 F8000 \n' %(xL))
        self.gfile.write('G0 X%.3f Y6.000 F8000 \n' %(xR) )
        self.gfile.write('G0 X%.3f Y6.000 F8000 \n' %(xL) )
        self.gfile.write('G0 X%.3f Y6.000 F8000 \n' %(xR) )

        self.gfile.write('G0 X%.3f Y%.3f F8000 \n' %(nextX, nextY))


    def initTool(self):
        self.gfile.write('G21                            ; Set unit to mm \n')
        self.gfile.write('T0\n')
        self.gfile.write('G90\n')
        self.gfile.write('G28                            ; Home \n')
        self.gfile.write('G92 E0                         ; Reset E \n')
        # setup index
        self.gfile.write('M163 S0 P%d                    ; Set extruder mix ratio B\n' %(self.ratioB))
        self.gfile.write('M163 S1 P%d                    ; Set extruder mix ratio A\n' %(self.ratioA))
        self.gfile.write('M163 S2 P0                     ; Enable Extruder \n')
        self.gfile.write('M83                            ; Relative extrusion mode\n')
        self.gfile.write('G1 Z15.0\n')

    def initJuggerBot(self):

        jRA = self.ratioA / 10000
        jRB = self.ratioB / 10000

        self.gfile.write('G21                            ; Set unit to mm \n')
        self.gfile.write('T2\n')
        self.gfile.write('G90\n')
        self.gfile.write('G28                            ; Home \n')
        self.gfile.write('G0 Z15.000 F1000\n')
        self.gfile.write('G30                            ; Single Z probe \n')
        self.gfile.write('G4 S2                          ; Pause for 2 sec\n')
        self.gfile.write('G29 S1 P"heightmap.csv"        ; Load bed map \n')
        self.gfile.write('G4 S2                          ; Pause for 2sec\n')
        self.gfile.write('G4 S2                          ; Pause for 2sec again \n')
        self.gfile.write('M98 P"/sys/SetZForPrinting.g"  ; Run macro to set tip height \n')
        self.gfile.write('M566 Z30.0                     ; Unknown command \n')
        self.gfile.write('M201 Z50.0                     ; Unknown command \n')
        self.gfile.write('G92 E0                         ; Reset E \n')
        # setup index
        self.gfile.write('M567 P2 E%.3f:%.3f                 ; Set extruder mix ratio A:B\n' %(jRA, jRB))
        self.gfile.write('M83                            ; Relative extrusion mode\n')


    def Generate(self):

        nPoint = len(self.rx)
        print(' total steps %d ' % ( nPoint ))

        for i in range(nPoint):

            xVal = self.rx[i] + self.sx
            yVal = self.ry[i] + self.sy
            zVal = self.rz[i] + self.sz
            eVal = self.rE[i]*self.sE
            fVal   = self.F*self.sF
            gfVal1 = self.gF1*self.sF
            gfVal2 = self.gF2*self.sF

            if i == 0 :
                self.gfile.write('G0 X%.3f Y%.3f F%.0f\n' %( xVal, yVal, fVal ) )

            if self.rs[i] == 1 :
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, fVal ) )

            if self.rs[i] == 0 :
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%0.0f\n' %( xVal, yVal, zVal, eVal, fVal  ) )

            if self.rs[i] == -2 :
                self.gfile.write( '; Retract Stop \n'  )
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f\n' %( xVal, yVal, zVal, eVal ) )

            if self.rs[i] == 2 :
                self.gfile.write( '; Retract Start \n'  )
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, fVal ) )
                #self.gfile.write( 'G4 P500\n' )
                self.gfile.write( '; Retract move \n'  )

            # status 3 and 4 is for gliding, slow down and giving lower extrude amount
            if self.rs[i] == 3 :
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal1 ) )

            if self.rs[i] == 4 :
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal2 ) )

            if self.rs[i] == 5 :
                self.gfile.write( '; move without extruding \n'  )
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%0.0f\n' %( xVal, yVal, zVal, 0., fVal  ) )

            # This is the finishing segment, stop extruding and slow down to 25% of speed
            if self.rs[i] == 9 :
                self.gfile.write( '; Ending section\n'  )
                self.gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, fVal/4 ) )

            if self.rs[i] == 99 :
                purgetime = eVal
                self.tipWipe( purgetime, xVal, yVal )

            if i == (nPoint -1) :
                self.gfile.write('G1 E-5.000\n')
                self.gfile.write('G4 P2000\n')
                self.gfile.write('G0 Z%.3f\n' %(self.rz[i]+50))



    def EndingGCode(self):

        self.gfile.write('; ---- Ending ---- \n')
        self.gfile.write('G1 E-5.000\n')
        self.gfile.write('G4 P2000\n')
        self.gfile.write('G0 X0.0 Y0.0\n')
        self.gfile.write('M104 S0\n')       # Disable Extruder
        self.gfile.write('M84 S0\n')        # Disable Motor
        self.gfile.close()


