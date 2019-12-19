import math

class GWords :

    xVal = 0
    yVal = 0
    zVal = 0
    eVal = 0
    fVal = 0
    rho  = 0
    moveType = 0
    gWords = []
    isG0G1 = False
    retract = False
    command = ''
    description = ''
    para = ''
    color = ''
    update = [0,0,0,0,0] # [x,y,z,e,f]

    def __init__(self):
        self.update = [0,0,0,0,0]

    def readline(self, gline ):
        self.gWords = gline.split()
        self.update = [0,0,0,0,0]
        self.eVal = 0.

    # update positions and rho
    def getPos(self, sx =0, sy =0, sz =0, sE = 1., sF = 1. ):

        if len( self.gWords ) < 1:
            print("No Entry")

        elif self.gWords[0]== 'G0' or self.gWords[0] == 'G1':

            self.isG0G1 = True

            dr = [0,0]
            for ig in self.gWords :
                #print( ' ig = '+ ig )
                if ig[0] == 'X':
                    iVal = float( ig[1:] )
                    if iVal != self.xVal :
                        dr[0] = iVal - self.xVal
                        self.xVal = iVal + sx
                        self.update[0] = 1
                if ig[0] == 'Y':
                    iVal = float( ig[1:] )
                    if iVal != self.yVal :
                        dr[1] = iVal - self.yVal
                        self.yVal = iVal + sy
                        self.update[1] = 1
                if ig[0] == 'Z':
                    iVal = float( ig[1:] )
                    if iVal != self.zVal :
                        self.zVal = iVal + sz
                        self.update[2] = 1
                if ig[0] == 'E':
                    iVal = float( ig[1:] )
                    if iVal != self.eVal :
                        self.eVal = iVal*sE
                        self.update[3] = 1

                    if float(self.eVal) <= 0. :
                        self.retract = True
                    else:
                        self.retract = False

                if ig[0] == 'F':
                    iVal = float( ig[1:] )
                    self.fVal = iVal*sF / 60.
                    self.update[4] = 1
            drMag = math.sqrt( (dr[0]*dr[0]) + (dr[1]*dr[1]) )
            if drMag > 0 :
                self.rho = self.eVal / drMag
            else :
                self.rho = 0.

            # Move Type is only defined by  first 3 bits (x,y,z)
            # if only x,y move , it will be 011 , which is 3
            # if only z move , it will be 100 , which is 4
            out = 0
            for bit in reversed(self.update) :
                out = ( out << 1 ) | bit

            # 7 is 111 in binary
            self.moveType = out & 7
            self.GetColor()

    def getCommand(self):

        if len( self.gWords ) < 1:
            print("No Entry")

        elif self.gWords[0][0] != ';':
            self.command = self.gWords[0]
            self.para    = self.gWords[1:]

        elif self.gWords[0][0] == ';':
            self.command = 'Comment'
            self.description = ' '.join(self.gWords)

    def posUpdated(self):

        move = False
        if sum( self.update[:4]) > 0 :
            move = True

        return move

    def GetColor(self):

        if self.command == 'G0' and self.moveType <= 3 :
            self.color = 'red'
        elif self.command =='G1' and self.eVal <= 0 and self.moveType <= 3 :
            self.color = 'orange'
        elif self.command == 'G1' and self.eVal > 0 and self.moveType <= 3 :
            self.color = 'blue'

        if self.moveType >= 4 :
            if self.retract :
                self.color = 'green'
            else :
                self.color = 'purple'




