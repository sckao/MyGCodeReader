import math
from GWords import GWords

# Rotate (x,y) CounterClockwise
#  |x|    [ cos   -sin ] | x0 |
#  |y| =  [ sin    cos ] | y0 |
def rotation( pos, theta, xc =0 , yc = 0 ) :

    x0 = pos[0] - xc
    y0 = pos[1] - yc
    x = x0*math.cos(theta) - y0*math.sin(theta)
    y = x0*math.sin(theta) + y0*math.cos(theta)
    x = x + xc
    y = y + yc
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

# flip g code w.r.t. a Y-axis
def flipY( pos , sx =0 , sy = 0, theta = 0) :

    imgV = []
    for i in range( len(pos) ) :

        x = pos[i][0]
        y = pos[i][1]

        xi = -1*x
        yi = y

        xr = xi*math.cos(theta) - yi*math.sin(theta)
        yr = xi*math.sin(theta) + yi*math.cos(theta)

        imgV.append( [xr + sx ,yr + sy ] )

    return imgV

# flip g code w.r.t. a X-axis
def flipX( pos , sx =0 , sy = 0, theta = 0) :

    imgV = []
    for i in range( len(pos) ) :

        x = pos[i][0]
        y = pos[i][1]

        yi = -1*y
        xi = x

        xr = xi*math.cos(theta) - yi*math.sin(theta)
        yr = xi*math.sin(theta) + yi*math.cos(theta)

        imgV.append( [xr + sx ,yr + sy ] )

    return imgV

def length( p1, p2 ) :

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr = math.sqrt( (dx*dx) + (dy*dy) )

    return dr

def shift( pos, dx, dy ) :

     pos[0] = pos[0] + dx
     pos[1] = pos[1] + dy

# rotate an outline
def rotateList( vec, n ) :

    vec1 = []
    closedLoop = False
    print(' sz of RT  %d ' %( len(vec)) )
    if vec[0] == vec[-1] :
        closedLoop = True
        print(' head tail same!')
        del vec[-1]
        vec1 = vec[n:] + vec[:n]
        #vec1.append( vec1[0] )
    else :
        vec1 = vec[n:] + vec[:n]

    if closedLoop is True :
        vec1.append(vec1[0])
        vec.append( vec[0] )
        print(' sz of RT %d, %d ' %(len(vec1), len(vec)) )

    return vec1

# This is the method to re-sort the sequence of a list based on the position of the empty element
# The list must has been insert an empty element [] for indication , the empty element will be removed after resort
def ReSort( vec ) :

    k = 0
    for i in range( len(vec)) :

        if vec[i] == [] :
            k = i
            break

    print(' len of vec = %d , at %d ' %(len(vec), k))
    del vec[k]
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

    if L21 == 0 or L32 == 0 :
        print( ' duplicated points !! Zero Degree Angle Return! ' )
        return 0

    cosA = axb / (L21*L32)
    #print(' cosA = %.3f' %(cosA) )
    if cosA <= -1.0 :
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

    if L13 == 0 :
        s = 999999999999
    else :
        s = abs(axb/L13)

    return s

def Reduce( v, turnLimit = math.pi/2, turnRange = 10, smin = 0.05, sRange = 0.2  ) :

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

        if angle > turnLimit  and L_ij < turnRange :
            del v[j]
            print('  delete big turning !!')
            j = j-1
            continue

        if sag < smin or L_ik < sRange :
            #print('  delete insignificant !!')
            del v[j]
            continue


        j = j+ 1

    print( ' --- to %d ' %( len(v)) )

# Read outline from a gcode
# Remove duplicated x,y position
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

            sameXY = False
            if len(v) > 0 :
                if v[-1][0] == xj and v[-1][1] == yj :
                    sameXY = True

            if len(v) < 1 or sameXY is False :
                v.append([xj, yj])

            #print(' shape [%d] (%.2f, %.2f)' %(i, xj, yj) )
            #i = i+1


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

