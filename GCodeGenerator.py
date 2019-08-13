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

    L = dLength( x1, y1, x2, y2 )
    dx = x2 -x1
    dy = y2 -y1
    x0 =  x2 - dx*ratio
    y0 =  y2 - dy*ratio
    return [x0,y0]


# rs status = 9 for ending
def Ending( flength, rs = [], rx = [], ry = [], rz = [], rE = [] ):

    j = len( rs ) - 1
    for i in range( len(rs) ) :

        L = dLength( rx[j], ry[j], rx[j-1], ry[j-1] )

        if L > flength :
            bp = BreakSegment( rx[j-1], ry[j-1], rx[j], ry[j], flength/L )
            ## re-calculate the E Value for the 1st segment
            dL = dLength(rx[j-1], ry[j-1], bp[0], bp[1] )
            eVal0 = rE[j] * dL / L

            rx.insert(j, bp[0])
            ry.insert(j, bp[1])
            rz.insert(j, rz[i])
            rE.insert(j, eVal0)
            rs.insert(j, 1)
            print(' == > ( %.3f, %.3f) -> ( %.3f, %.3f)  in %.4f (%d)' %( rx[j-1], ry[j-1], rx[j], ry[j], eVal0, rs[j]))
            ## re-calculate the E Value for the 2nd segment
            dL = dLength(rx[j+1], ry[j+1], bp[0], bp[1] )
            rE[j+1] = 0
            rs[j+1] = 9
            print(' ===> ( %.3f, %.3f) -> ( %.3f, %.3f) ' %( rx[j + 1], ry[j + 1], rx[j], ry[j]))
            break
        else :
            rE[j] = 0
            rs[j] = 9

        j = j -1



class GCodeGenerator :

    # Linear density ( or Flow rate )
    rho = 0.75
    Fval = 6000.
    Eval = Fval*rho


    def __init__(self, rs = [], rx =[], ry=[], rz=[], rE=[], F =4000 ):

        self.rs = rs
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.rE = rE
        self.F   = F
        self.gF1 = F
        self.gF2 = F

        self.sx = 0
        self.sy = 0
        self.sz = 0
        self.sE = 1
        self.sF = 1


    def Shift(self, sx0 = 0., sy0 = 0. , sz0 = 0., sE0 = 1., sF0 = 1. ):

        self.sx = sx0
        self.sy = sy0
        self.sz = sz0
        self.sE = sE0
        self.sF = sF0

    def SetGlideSpeed(self, F1 , F2 ):
        self.gF1 = F1
        self.gF2 = F2


    def Retract(self, up = 2, down = 2, rS = [], rx = [], ry = [], rz = [], rE = []  ):

             i = len( rx ) -1
             rx.append( rx[i] )
             ry.append( ry[i] )
             rz.append( rz[i]+ up  )
             rE.append( -1  )
             rS.append( 2 )


    def Gliding(self, gTime1, eRatio1 , gTime2, eRatio2, rS = [], rx = [], ry = [], rz = [], rE = [] ):

        # gd: Gliding distance (mm) : Def by  x sec in whatever speed ( mm/sec )
        gd1 = gTime1 * self.gF1 / 60.
        gd2 = gTime2 * self.gF2 / 60.
        print(' Start Gliding rS size = %d -> %.3f , %.3f' % (len(rS), gd1, gd2))

        doGlide = False
        i = 0
        for it in rS:

            print(' SIZE = %d' % (len(rS)))
            if it == 0 or abs(it) == 2:
                i = i + 1
                continue

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


    def Generate(self):

        # Open a text file
        gfilename = input('Generated GCode filename : ')
        if gfilename == '':
            gfilename = 'gout.gcode'
        gfile = open(gfilename, 'w')

        nPoint = len(self.rx)
        print(' total steps %d ' % ( nPoint ))

        xVal = self.rx[0]
        yVal = self.ry[0]
        zVal = self.rz[0]
        eVal = self.rE[0]
        fVal = self.F
        gfVal1 = self.gF1
        gfVal2 = self.gF2


        for i in range(nPoint):

            xVal = self.rx[i] + self.sx
            yVal = self.ry[i] + self.sy
            zVal = self.rz[i] + self.sz
            eVal = self.rE[i]*self.sE
            fVal   = self.F*self.sF
            gfVal1 = self.gF1*self.sF
            gfVal2 = self.gF2*self.sF

            if i == 0 :
                gfile.write('G90\n')
                gfile.write('M83\n')
                gfile.write('M106 S0\n')
                gfile.write('G28\n')
                gfile.write('T0\n')
                gfile.write('G1 Z15.0\n')
                gfile.write( 'G0 X%.3f Y%.3f F%.0f\n' %( xVal, yVal, fVal ) )

            if self.rs[i] == 1 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, fVal ) )

            if self.rs[i] == 0 :
                gfile.write( 'G0 X%.3f Y%.3f Z%.3f E%.4f\n' %( xVal, yVal, zVal, eVal  ) )

            if abs(self.rs[i]) == 2 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f\n' %( xVal, yVal, zVal, eVal ) )

            # status 3 and 4 is for gliding, slow down and giving lower extrude amount
            if self.rs[i] == 3 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal1 ) )

            if self.rs[i] == 4 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal2 ) )

            # This is the finishing segment, stop extruding and slow down to 25% of speed
            if self.rs[i] == 9 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, fVal/4 ) )


            if i == (nPoint -1) :
                gfile.write('G1 E-1.5000\n')
                gfile.write('G0 Z%.3f\n' %(self.rz[i]+10))
                gfile.write('G0 X0.0 Y0.0\n')
                gfile.write('M104 S0\n')       # Disable Extruder
                gfile.write('M84 S0\n')        # Disable Motor



        gfile.close()

