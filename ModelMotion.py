import math
from GWords import GWords

# Rotate (x,y) CounterClockwise
#  |x|    [ cos   -sin ] | x0 |
#  |y| =  [ sin    cos ] | y0 |
def rotation( pos, theta ) :

    x0 = pos[0]
    y0 = pos[1]
    x = x0*math.cos(theta) - y0*math.sin(theta)
    y = x0*math.sin(theta) + y0*math.cos(theta)
    pos[0] = x
    pos[1] = y

    return x,y

# Incorrect - Obsolete
def zoom( pos, scale ) :

    x0 = pos[0]
    y0 = pos[1]
    r0 = math.sqrt( (x0*x0) + (y0*y0) )
    cos = x0/r0
    sin = y0/r0

    r = r0*scale
    x = r*cos
    y = r*sin
    pos[0] = x
    pos[1] = y

def shift( pos, dx, dy ) :

     pos[0] = pos[0] + dx
     pos[1] = pos[1] + dy

def rotateList( vec, n ) :

    return vec[n:] + vec[:n]

def ReSort( vec ) :

    k = 0
    for i in range( len(vec)) :

        if vec[i] == [] :
            k = i
            break

    vec1 = rotateList(vec, k)

    #for it in vec1 :
    #    if it == [] :
    #        print(' 1st ! ')
    #    else :
    #        print( ' %.2f, %.2f'  %(it[0], it[1]) )

    return vec1


# Read outline from a gcode
def ReadOutline( fileName, sx, sy, theta  ) :
    # Read GCode File

    if fileName == '' :
        fileName = input('Read filename : ')

    f = open(fileName, 'r+')

    gd = GWords()
    v = []
    i = 0
    for line in f:

        if len(line) < 1:
            continue

        # 1. Read line from the file
        gd.readline(line)

        # 2. Get command ( G, M or ... )
        gd.getCommand()
        cmd = gd.command

        # 3. Get X Y Z E F
        gd.getPos()

        if gd.posUpdated():

            xi = gd.xVal
            yi = gd.yVal
            if gd.xVal ==0  and gd.yVal == 0 :
                continue

            pos = [xi,yi]
            rotation( pos, theta )
            shift( pos, sx, sy )

            xj = pos[0]
            yj = pos[1]


            print(' shape [%d] (%.2f, %.2f)' %(i, xj, yj) )
            v.append([xj, yj])
            i = i+1


    if len(v) > 0 :
        vx0 = v[0][0]
        vy0 = v[0][1]
        vx1 = v[-1][0]
        vy1 = v[-1][1]

        if vx0 == vx1 and vy0 == vy1 :
            print(' Closed Loop !' )
        else :
            v.append( [v[0][0], v[0][1]] )
            print(' NOT Closed Loop !' )

    return v

