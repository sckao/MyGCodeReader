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

def length( p1, p2 ) :

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr = math.sqrt( (dx*dx) + (dy*dy) )

    return dr

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

# Return angle between 0 ~ pi
def turnAngle( p1, p2, p3 ) :

    v21_x = p2[0] - p1[0]
    v21_y = p2[1] - p1[1]

    v32_x = p3[0] - p2[0]
    v32_y = p3[1] - p2[1]

    axb = (v21_x*v32_x) + (v21_y*v32_y)
    L21 = length( p2, p1 )
    L32 = length( p3, p2 )

    cosA = axb / (L21*L32)
    print(' cosA = %.2f' %(cosA) )
    if cosA == -1 :
        angle = math.pi
    else :
        angle = math.acos( cosA )

    return angle

# find the distance between p2 and line p1-p3
# p1, p2, p3 are [x,y] format
def sagitta( p1, p2, p3 ) :

    v21_x = p2[0] - p1[0]
    v21_y = p2[1] - p1[1]

    v31_x = p3[0] - p1[0]
    v31_y = p3[1] - p1[1]

    axb = (v21_x*v31_y) -  (v21_y*v31_x)
    L13 = length( p1, p3 )

    s = abs(axb/L13)

    return s

def Reduce( v, smin = 0.05 ) :

    print( 'Reduce v from %d ' %( len(v)) )
    j = 1
    while j < len(v)-1 :

        i = j - 1
        k = j + 1

        L_ik = length( v[i], v[k] )
        L_ij = length( v[i], v[j] )
        sag = sagitta( v[i], v[j], v[k] )
        angle = turnAngle( v[i], v[j], v[k] )
        #print( ' Lik = %.2f , Lij = %.2f , sag = %.2f , angle = %.2f ' %(L_ik, L_ij, sag, angle) )
        #if angle > ( math.pi/2 ) :
        #    print(' Large angle = %.2f / Lij = %.2f' %(angle*180/math.pi , L_ij))

        if angle > math.pi/2  and L_ij < 10 :
            del v[j]
            print('  delete big turning !!')
            j = j-1
            continue

        if sag < smin or L_ik < 0.2 :
            #print('  delete insignificant !!')
            del v[j]
            continue


        j = j+ 1

    print( ' --- to %d ' %( len(v)) )

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


            #print(' shape [%d] (%.2f, %.2f)' %(i, xj, yj) )
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

