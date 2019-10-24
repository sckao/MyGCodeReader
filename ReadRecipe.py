

class ReadRecipe :


    def __init__(self):

        self.Fval = 1000
        self.rho = 0.6
        self.nLayer = 1
        self.bh = 0.5
        self.ts = 0.35
        self.fh = 0.0
        self.bs = 1.5
        self.rh = 5

        recipename = input('Recipe filename : ')
        if recipename == '':
            recipename = 'recipe.txt'

        self.recipe = open(recipename, 'r+')
        self.rlines = self.recipe.readlines()


    # Get parameters from the recipe file
    # ParameterName = value
    # ParameterName = value1, value2, value3, ...
    # ParameterName = [ string1, string2, string3, ... ]
    # parameter will be transfered to float type
    # if values are bracketed in [ ] , they will be retained as string
    def getParameter(self, paraName ):


        isString = False
        for line in self.rlines :

            if line[0] == '#' :
                continue

            id = line.find( paraName )
            # exclucde the case when the paraName is the sub-string of other paraName
            if id > 0 and id < 999 and line[id-1] != ' ' :
                continue
            if id < 0 :
                continue

            # Find the value of the parameter
            sid = id + len(paraName)
            sline = line[sid:]
            vid = sline.find('=')
            if vid < 0 :
                print(' No value assignment !!! - ' + sline )
                continue

            # strip off '=' and get the values
            vline = sline[vid+1:]

            # To identify whether the parameter is string or not
            h = vline.find('[')
            t = vline.find(']')
            if h >= 0 and t > h :
                vline = vline[h+1:t]
                isString = True
            else :
                isString = False

            vals = vline.split(',')
            break


        # Transfer reading values to the proper type

        if len(vals) > 1 :
            vlist = []
            for it in vals :
                if isString :
                    vlist.append( it )
                else :
                    vlist.append( float(it) )

            return vlist

        elif len(vals) == 1 :
            val = float(vals[0])
            return val
        else :
            return


    # Function to get basic 8 printing parameters
    def getPrintable(self):

        paraNames = [ 'PrintSpeed', 'FlowRate', 'NLayer', 'BeadHeight', 'TipSpacing', 'FirstHeight', 'BeadSpacing', 'RetractHeight' ]

        for line in self.rlines :

            if line[0] == '#' :
                continue

            for iPar in paraNames :
                id =  line.find(iPar)

                # exclucde the case when the paraName is the sub-string of other paraName
                if id > 0 and id < 999 and line[id-1] != ' ' :
                    print('Not Parameter - ' + iPar )
                    continue
                if id < 0 :
                    print('Missing Parameter - ' + iPar )
                    continue

                # Find the value of the parameter
                sid = id + len( iPar)
                sline = line[sid:]
                vid = sline.find('=')
                if vid < 0 :
                    print(' No value assignment !!! - ' + sline )
                    continue

                # strip off '=' and get the values
                vline = sline[vid+1:]
                vals = vline.split(',')

                # Transfer reading values to the proper type
                print('Update data')
                if iPar == 'PrintSpeed' :
                    self.Fval = float(vals[0])
                if iPar == 'FlowRate' :
                    self.rho = float(vals[0])
                if iPar == 'NLayer' :
                    self.nLayer = float(vals[0])
                if iPar == 'BeadHeight' :
                    self.bh = float(vals[0])
                if iPar == 'TipSpacing' :
                    self.ts = float(vals[0])
                if iPar == 'FirstHeight' :
                    self.fh = float(vals[0])
                if iPar == 'BeadSpacing' :
                    self.bs = float(vals[0])
                if iPar == 'RetractHeight' :
                    self.rh = float(vals[0])


    def showPrintable(self):

        #self.getPrintable()

        print(' 0 PrintSpeed  = %.0f'  %(self.Fval) )
        print(' 1 Flow Rate   =  %.3f' %(self.rho) )
        print(' 2 NLayer      =  %.0f' %(self.nLayer) )
        print(' 3 Bead Height =  %.3f' %(self.bh) )
        print(' 4 Tip Spacing =  %.3f' %(self.ts) )
        print(' 5 First Height =  %.3f' %(self.fh) )
        print(' 6 Bead Spacing =  %.3f' %(self.bs) )
        print(' 7 Retract Height =  %.3f' %(self.rh) )
