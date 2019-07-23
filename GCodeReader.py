import numpy as np
import math
import os
from GCodePaser import GWords
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



# Read files and out put GCode results
fname    = input('Read filename : ')
foutname = input('Write filename : ')
if foutname == '' :
    foutname = 'out.txt'
gfilename = input('Output GCode filename : ')
if gfilename != '' :
    gfile = open( gfilename, 'w' )


f = open(fname, 'r+')
fout = open( foutname, 'w')

fout.write( ' id,  X,  Y,  Z,  dr,  rho,  E,  sumL \n' )

# position and color list for drawing plots
v = []
h = []
cl = []
hcl = []

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
    # Get command ( G, M or ... )
    gd.getCommand()
    cmd = gd.command
    # Get X Y Z E F
    gd.getPos()
    SaveNewGCode( gfile, gd)

    if cmd == 'G28':
        print(' Home - Initialized ' + cmd +' \n')

    #if line[0:7] == '; layer':
    #    print(' NEXT Layer !!!\n')

    if  gd.posUpdated() :

        # Record each position
        v.append( [gd.xVal, gd.yVal] )
        dz =  gd.zVal - z0

        if dz == 0. and gd.eVal > 0. and zL != gd.zVal :
            zL = gd.zVal
            print('Change Layer Height ={:.3f} \n'.format(zL))
            Flush = True


        # Sum over all movement
        if i > 0 :
            v_dr = makeV( v[i], v[i-1] )
            dr = vMag( v_dr )

            if gd.eVal > 0. :
               totalL += dr
               dL += dr

            if dr != 0. and gd.eVal > 0. :
                rho = gd.eVal / dr
            else :
                rho = 0.


        # Color different movement
        if cmd == 'G0':
            cl.append( 'red' )
        elif cmd =='G1' and gd.eVal <= 0 :
            cl.append( 'green' )
        else :
            cl.append( 'blue' )

        # Record Z movement
        if gd.update[2] != 0 :
            h.append( [ gd.xVal, gd.yVal ] )
            hcl.append( 'red' )
            z0 = gd.zVal
            #print(' move Z = {:.3f} '.format(dz) + ' Z = {:.3f}'.format(gd.zVal) + ' dr = {:.3f}'.format(dr) + ' E = {:.3f}'.format(gd.eVal) )
            # Reset dL if z is changed
            dL = 0.

        # output            x, y, z, dr, rho, E, dL
        if i == 0 :
            fout.write( '; Change Layer Height ={:.3f} \n'.format(zL) )

        fout.write( '{:5d}'.format(i) +', {:.3f}'.format(v[i][0]) + ', {:.3f}'.format(v[i][1]) + ', {:.3f}'.format(gd.zVal) +', {:.3f}'.format(dr) + ', {:.3f}'.format(rho) + ', {:.4f}'.format(gd.eVal)+ ', {:.3f}'.format(dL) + '\n' )
        #fout.write( '{:.3f}'.format(gd.xVal) + ',{:.3f}'.format(gd.yVal) + ', {:.3f}'.format(gd.zVal) + ', {:.4f}'.format(gd.eVal)+ ',{:.4f}'.format(gd.fVal) + '\n' )
        # Save New GCode
        SaveNewGCode( gfile, gd)

        # E value < 0, Z movement only
        if gd.retract  and gd.update[2] != 0 :
            print(' Retract ' + ' x= {:.3f}'.format(gd.xVal) + ' y= {:.3f}'.format( gd.yVal ) + ' z= {:.3f}'.format( gd.zVal ) +  ' e= {:.3f}'.format(gd.eVal) )
            h.append( [ gd.xVal, gd.yVal] )
            hcl.append( 'black' )

        i = i+1


    if cmd == 'M84':
        Flush = True
        fout.write('{:.3f}'.format(totalL) + '\n' )

    if Flush :

        print('This layer has %d vector and %d Z movement ' %(len(v), len(h)) )
        ShowPath(v, cl, h, hcl )
        v = []
        cl = []
        h = []
        hcl = []
        i = 0
        Flush = False


f.close()
fout.close()
gfile.close()

