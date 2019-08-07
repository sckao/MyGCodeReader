
class GCodeGenerator :

    def __init__(self, rs = [], rx =[], ry=[], rz=[], rE=[], F =4000 ):

        self.rs = rs
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.rE = rE
        self.F   = F
        self.gF1 = F
        self.gF2 = F



    def Shift(self, sx0 = 0., sy0 = 0. , sz0 = 0., sE0 = 1., sF0 = 1. ):

        self.sx = sx0
        self.sy = sy0
        self.sz = sz0
        self.sE = sE0
        self.sF = sF0

    def SetGlideSpeed(self, F1 , F2 ):
        self.gF1 = F1
        self.gF2 = F2

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

            if self.rs[i] == 3 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal1 ) )

            if self.rs[i] == 4 :
                gfile.write( 'G1 X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( xVal, yVal, zVal, eVal, gfVal2 ) )


            if i == (nPoint -1) :
                gfile.write('G1 E-1.5000\n')
                gfile.write('G0 Z%.3f\n' %(self.rz[i]+10))
                gfile.write('G0 X0.0 Y0.0\n')
                gfile.write('M104 S0\n')       # Disable Extruder
                gfile.write('M84 S0\n')        # Disable Motor



        gfile.close()
