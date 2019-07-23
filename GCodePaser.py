
class GWords :

    xVal = 0
    yVal = 0
    zVal = 0
    eVal = 0
    fVal = 0
    gWords = []
    isG0G1 = False
    retract = False
    command = ''
    para = ''
    update = [0,0,0,0,0] # [x,y,z,e,f]

    def __init__(self):
        self.update = [0,0,0,0,0]

    def readline(self, gline ):
        self.gWords = gline.split()
        self.update = [0,0,0,0,0]
        self.eVal = 0.

    def getPos(self):

        if len( self.gWords ) < 1:
            print("No Entry")

        elif self.gWords[0]== 'G0' or self.gWords[0] == 'G1':

            self.isG0G1 = True

            for ig in self.gWords :
                if ig[0] == 'X':
                    self.xVal = float(ig[1:])
                    self.update[0] = 1
                if ig[0] == 'Y':
                    self.yVal = float(ig[1:])
                    self.update[1] = 1
                if ig[0] == 'Z':
                    self.zVal = float(ig[1:])
                    self.update[2] = 1
                if ig[0] == 'E':
                    self.eVal = float(ig[1:])
                    self.update[3] = 1
                    if float(self.eVal) < 0. :
                        self.retract = True
                    else:
                        self.retract = False
                if ig[0] == 'F':
                    self.fVal = float(ig[1:]) / 60.
                    self.update[4] = 1

    def getCommand(self):

        if len( self.gWords ) < 1:
            print("No Entry")

        elif self.gWords[0][0] != ';':
            self.command = self.gWords[0]
            self.para    = self.gWords[1:]

        elif self.gWords[0][0] == ';':
            self.command = 'Comment'

    def posUpdated(self):

        move = False
        if sum( self.update[:3]) > 0 :
            move = True

        return move
