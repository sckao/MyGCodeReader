import numpy as np
import math
from GWords import GWords
from GCodeViewer import ShowPath, vMag

###############################
#       Color Code
#  black : home vector
#  blue  : G1 , E > 0
#  Green : G1 , E <= 0
#  red   : G0 vector
#
###############################

def makeV( p1, p2 ):

    q = [ p2[i]-p1[i] for i in range(2)]
    #q = [0,0]
    #for i in range(2):
    #    print( str(i) + ") " + str(p1[i]) + " " + str(p2[i]) )
    #    q[i] = p2[i] - p1[i]

    return q

def derivative(v1, v2):

    v1Mag = vMag( v1 )
    v2Mag = vMag( v2 )

    dv= [0,0]
    if v1Mag > 0 and v2Mag > 0:
        v1n = [ i/v1Mag for i in v1 ]
        v2n = [ i/v2Mag for i in v2 ]

        for i in range(2) :
            dv[i] = v2n[i] - v1n[i]
        return dv
    else :

        return dv

def SaveNewGCode( gfile, cmd, para, descript ):

    #if os.path.exists( gfile) : return

    para1 = ''
    for i in para :
        para1 = para1 + ' ' + i

    if  cmd == 'Comment' :
        gfile.write( descript +   '\n' )

    elif  cmd != 'G0' and cmd != 'G1' :
        gfile.write( cmd + para1 + '\n' )

    else :
        pass

    #elif cmd == 'G0' or cmd == 'G1' :
    #    if gword.update[4] == 1 :
    #        gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal, gword.fVal*60) )
    #    else :
    #        gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal) )


def getRho( pos1, pos2, Eval ) :

    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    dr = math.sqrt( (dx*dx) + (dy*dy) )

    rho = 0
    if dr > 0. :
        rho = Eval/dr

    return rho, dr
#                   0     1     2    3      4        5    6   7    8
# vlist format : [  ax,   y,    z,   E,  color, moveType, F, cmd, rho ]
# clist format " [ idx, cmd, para, description ]
def SaveThisLayer( gfile, vlist, cList, lastLayer = False ) :


    nStep = len(vlist)
    for i in range( nStep ):


        if i > nStep-3 and lastLayer is False :
            break

        it = vlist[i]
        if i > 0 :
            rho, dr = getRho( it, vlist[i-1], it[3] )

            if rho != it[8] :
                print(' rho mismatch : %.2f -> %.2f ' %(it[8], rho) )
                it[3] = dr*it[8]

        cmd = it[7]
        if cmd != 'G28':
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %( it[0], it[1], it[2], it[3], it[6]*60 ) )

        for jt in cList :
            if jt[0] == i :
                #print(' i = %d , idx cmd = %d ' %(i, jt[0]) + jt[1] )
                SaveNewGCode(gfile, jt[1], jt[2], jt[3] )


def ReadGFile() :

    fname    = input('Read filename : ')
    f = open(fname, 'r+')

    vlines = []
    for line in f:

        #print(line, end='')
        if len( line ) < 1 :
            print( ' line size = ' + str( len(line)) )
            continue

        # Keep the line
        vlines.append(line)

        # Find out actual z slice position
        #words = line.split()
        #if words[0] == 'G0' or words[0] == 'G1' :
        #    for ig in words :
        #        if ig[0] == Z :
        #            z = float(ig[1:])


    return vlines


##############################################
#           Main : Start Reading             #
##############################################

# Read GCode File
fname    = input('Read filename : ')
f = open(fname, 'r+')

# Log file
foutname = 'out.txt'
fout = open( foutname, 'w')

# New GCode file
gfilename = input('Output GCode filename : ')
if gfilename == '' :
    gfilename = 'gout.gcode'

gfile = open( gfilename, 'w' )

fout.write( '   id,     X,     Y,     Z,    dr,    rho,    E,    sumL \n' )

# position and color list for drawing plots
# x,y,z,E,color,
v = []
# other command in-between the same layer
cmdList = []

i = 0
z0 = 0.
zL = 0.
dz = 0.
dL = 0.
dr = 0.
# Total Print length
totalL = 0.
# linear density
rho = 0.
gd = GWords()
Flush = False

k = 0
# z0 : previous z position , zL : Layer z position, will be detected if E > 0
for line in f:

    if len( line ) < 1 :
        continue

    # 1. Read line from the file
    gd.readline( line )
    if gd.posUpdated() :
       print( " A %d - XYZ moved ! " %(i))

    # 2. Get command ( G, M or ... )
    gd.getCommand()
    cmd = gd.command
    para = gd.para
    descript = gd.description

    # 3. Get X Y Z E F
    gd.getPos()
    #SaveNewGCode( gfile, gd)

    # 4. Record other commands and comments
    if cmd != 'G1' and cmd != 'G0' :
        print(' (%d) cmd = '%(i) + cmd )
        cmdList.append( [i, cmd, para, descript ] )

    # 5. Add home position as starting point
    if cmd == 'G28':
        #print(' Home - Initialized ' + cmd +' \n')
        v.append( [ 0, 0, 0, 0, 'black', 0, gd.fVal, cmd, 0 ] )

    # 6. Check position if one of x,y,z moved
    #    Detect layer change
    if  gd.posUpdated() :

        # Record each position and motion type(3bit for x,y,z) with its color code
        v.append( [gd.xVal, gd.yVal, gd.zVal, gd.eVal, gd.color, gd.moveType, gd.fVal, cmd, gd.rho ] )
        dz =  gd.zVal - z0

        # Identify layer change
        if dz == 0. and gd.eVal > 0. and zL != gd.zVal :
            zL = gd.zVal
            print('Change Layer Height ={:.3f} \n'.format(zL))
            Flush = True

        # Record Z movement
        if gd.update[2] != 0 :
            z0 = gd.zVal
            #print(' move Z = {:.3f} '.format(dz) + ' Z = {:.3f}'.format(gd.zVal) + ' dr = {:.3f}'.format(dr) + ' E = {:.3f}'.format(gd.eVal) )
            # Reset dL if z is changed
            dL = 0.
            # Identify retraction - E value < 0 + with Z movement
            if gd.retract and dz > 0 :
                fout.write( '; Retract Start \n' )
            if gd.retract and dz < 0. :
                fout.write( '; Retract End \n' )
                print(' Retract ' + ' x= {:.3f}'.format(gd.xVal) + ' y= {:.3f}'.format( gd.yVal ) + ' z= {:.3f}'.format( gd.zVal ) +  ' e= {:.3f}'.format(gd.eVal) )

        # Sum over all movement
        if i > 0 :
            k = len(v)
            v_dr = makeV( v[k-1], v[k-2] )
            dr = vMag( v_dr )
            fout.write(' v (%.3f, %.3f) \n' %(v_dr[0], v_dr[1]))

            if gd.eVal > 0. :
               totalL += dr
               dL += dr

        # output            x, y, z, dr, rho, E, dL
        if i == 0 :
            fout.write( '; Change Layer Height = {:.3f} \n'.format(zL) )
            #gfile.write('; Layer Changed = {:.3f} \n'.format(zL) )

        fout.write( '{:5d}'.format(i) +', {:.3f}'.format(gd.xVal) + ', {:.3f}'.format(gd.yVal) + ', {:.3f}'.format(gd.zVal) +', {:.3f}'.format(dr) + ', {:.3f}'.format(gd.rho) + ', {:.4f}'.format(gd.eVal)+ ', {:.3f}'.format(dL) + '\n' )
        #fout.write( '{:.3f}'.format(gd.xVal) + ',{:.3f}'.format(gd.yVal) + ', {:.3f}'.format(gd.zVal) + ', {:.4f}'.format(gd.eVal)+ ',{:.4f}'.format(gd.fVal) + '\n' )

        i = i+1

    # Draw the layer and save any gcode change to a new gcode file
    if Flush :
        print(' This layer has %d vector, %d commands ' %( len(v), len(cmdList) ) )
        ShowPath( v, gfile )
        SaveThisLayer( gfile, v , cmdList )
        # The last element belong to next layer, so keep it and show it in the next layer
        vlast = v[-1]
        vlast2 = v[-2]
        print(' Last element %.3f %.3f %.3f %.4f' %(vlast[0], vlast[1], vlast[2], vlast[3] ))
        v = []
        cmdList = []
        v.append( vlast2 )
        v.append( vlast )
        i = 1
        Flush = False

    if cmd == 'M84':
        Flush = True
        print(' This layer has %d vector, %d commands ' %( len(v), len(cmdList) ) )
        ShowPath( v, gfile )
        SaveThisLayer( gfile, v, cmdList, True )
        fout.write('{:.3f}'.format(totalL) + '\n' )


f.close()
fout.close()
gfile.close()

