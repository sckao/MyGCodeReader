from GWords import GWords
#from GCodeViewer import ShowPath, vMag

def makeV( p1, p2 ):

    q = [ p2[i]-p1[i] for i in range(2)]
    #q = [0,0]
    #for i in range(2):
    #    print( str(i) + ") " + str(p1[i]) + " " + str(p2[i]) )
    #    q[i] = p2[i] - p1[i]

    return q


def SaveNewGCode( gfile, gword ):

    #if os.path.exists( gfile) : return

    cmd = gword.command
    para = ''
    for i in gword.para :
        para = para + ' ' + i

    if  cmd == 'Comment' :
        gfile.write( gword.description + '\n' )
        return
    elif  cmd != 'G0' and cmd != 'G1' :
        gfile.write( cmd + para + '\n' )
    elif cmd == 'G0' :
        if gword.update[4] == 1 :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f F%.0f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.fVal*60) )
        else :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f\n' %(gword.xVal, gword.yVal, gword.zVal ) )
    elif cmd == 'G1' :
        if gword.update[4] == 1 :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal, gword.fVal*60) )
        else :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal) )


##############################################
#           Main : Start Reading             #
##############################################

# Read files and output GCode results
fname    = input('Read filename : ')

gfilename = input('Output GCode filename : ')
if gfilename == '' :
    gfilename = 'gout.gcode'

shift_x = input(' Shift X (0) : ')
if shift_x == '':
    shift_x = 0
else:
    shift_x = float( shift_x )

shift_y = input(' Shift Y (0) : ')
if shift_y == '':
    shift_y = 0
else:
    shift_y = float( shift_y )

shift_z = input(' Shift Z (0) : ')
if shift_z == '':
    shift_z = 0
else:
    shift_z = float( shift_z )

f = open(fname, 'r+')
gfile = open( gfilename, 'w' )


# position and color list for drawing plots
v = []

i = 0
z0 = 0.
zL = 0.
dz = 0.
dL = 0.
dr = 0.
# Total Print length
totalL = 0.
# line density
rho = 0.
gd = GWords()
Flush = False

# z0 : previous z position , zL : Layer z position, will be detected if E > 0
for line in f:

    if len( line ) < 1 :
        print( ' line size = ' + str( len(line)) )
        continue

    # Read line from the file
    gd.readline( line )

    # Get command ( G, M or ... )
    gd.getCommand()
    cmd = gd.command

    # Get X Y Z E F
    gd.getPos(shift_x, shift_y, shift_z)

    # Update new gcode
    SaveNewGCode( gfile, gd)


f.close()
gfile.close()

