import numpy as np
import math
from GWords import GWords
from GCodeViewer import ShowPath, vMag

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
        print( ' zero mag \n')
        return dv

def SaveNewGCode( gfile, gword ):

    #if os.path.exists( gfile) : return

    cmd = gword.command
    para = ''
    for i in gword.para :
        para = para + ' ' + i

    if  cmd == 'Comment' :
        return
    elif  cmd != 'G0' and cmd != 'G1' :
        gfile.write( cmd + para + '\n' )
    elif cmd == 'G0' or cmd == 'G1' :
        if gword.update[4] == 1 :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f F%.0f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal, gword.fVal*60) )
        else :
            gfile.write( cmd + ' X%.3f Y%.3f Z%.3f E%.4f\n' %(gword.xVal, gword.yVal, gword.zVal, gword.eVal) )


##############################################
#           Main : Start Reading             #
##############################################

# Read files and output GCode results
fname    = input('Read filename : ')

foutname = input('Write filename : ')
if foutname == '' :
    foutname = 'out.txt'

gfilename = input('Output GCode filename : ')
if gfilename == '' :
    gfilename = 'gout.gcode'

f = open(fname, 'r+')
fout = open( foutname, 'w')
gfile = open( gfilename, 'w' )

fout.write( '   id,     X,     Y,     Z,    dr,    rho,    E,    sumL \n' )

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
    #print(line, end='')

    if len( line ) < 1 :
        print( ' line size = ' + str( len(line)) )
        continue

    # Read line from the file
    gd.readline( line )
    if gd.posUpdated() :
       print( " A %d - XYZ moved ! " %(i))
    # Get command ( G, M or ... )
    gd.getCommand()
    cmd = gd.command
    # Get X Y Z E F
    gd.getPos()
    SaveNewGCode( gfile, gd)

    if cmd == 'G28':
        print(' Home - Initialized ' + cmd +' \n')
        v.append( [ 0, 0, 0, 0, 'black', 0 ] )

    # if one of x,y,z moved
    if  gd.posUpdated() :
        #print( " B %d - XYZ [%d , %d , %d] ! " %(i, gd.update[0], gd.update[1], gd.update[2]))
        #print( " = XYZ [%.3f , %.3f , %.3f,  %.3f] ! " %( gd.xVal, gd.yVal, gd.zVal, gd.eVal))

        # Record each position and motion type with its color code
        v.append( [gd.xVal, gd.yVal, gd.zVal, gd.eVal, gd.color, gd.moveType ] )
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

            if dr != 0. and gd.eVal > 0. :
                rho = gd.eVal / dr
            else :
                rho = 0.


        # output            x, y, z, dr, rho, E, dL
        if i == 0 :
            fout.write( '; Change Layer Height = {:.3f} \n'.format(zL) )
            gfile.write('; Layer Changed = {:.3f} \n'.format(zL) )

        fout.write( '{:5d}'.format(i) +', {:.3f}'.format(gd.xVal) + ', {:.3f}'.format(gd.yVal) + ', {:.3f}'.format(gd.zVal) +', {:.3f}'.format(dr) + ', {:.3f}'.format(rho) + ', {:.4f}'.format(gd.eVal)+ ', {:.3f}'.format(dL) + '\n' )
        #fout.write( '{:.3f}'.format(gd.xVal) + ',{:.3f}'.format(gd.yVal) + ', {:.3f}'.format(gd.zVal) + ', {:.4f}'.format(gd.eVal)+ ',{:.4f}'.format(gd.fVal) + '\n' )

        i = i+1

    if Flush :
        print(' This layer has %d vector ' %( len(v) ) )
        ShowPath( v, gfile )
        # The last element belong to next layer, so keep it and show it in the next layer
        vlast = v[-1]
        vlast2 = v[-2]
        print(' Last element %.3f %.3f %.3f %.4f' %(vlast[0], vlast[1], vlast[2], vlast[3] ))
        v = []
        v.append( vlast2 )
        v.append( vlast )
        i = 0
        Flush = False

    if cmd == 'M84':
        Flush = True
        print('This layer has %d vector ' %( len(v) ) )
        ShowPath( v, gfile )
        fout.write('{:.3f}'.format(totalL) + '\n' )


f.close()
fout.close()
gfile.close()

