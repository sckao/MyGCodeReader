import numpy as np
import plotly
import plotly.plotly as plt
import plotly.figure_factory as ff
import plotly.graph_objs as go

import math

from plotly.offline import init_notebook_mode

def vMag( vec ):
    len =  math.sqrt( (vec[0]*vec[0]) + (vec[1]*vec[1]) )
    return len


#def ShowVectors( gV, colorV, hV, hCol ):
def ShowVectors( gV ):


    plotly.tools.set_credentials_file( username='kaoshihchuan', api_key='AHpO2zYe4pzOOddMe4nz' )

    init_notebook_mode( connected= True )

    # Getting data points
    '''

    sX = []
    sY = []
    sC = []
    rX = []
    rY = []
    rC = []
    for i in range( len(hV) ):
        if  hCol[i] == 'red' :
            sX.append( hV[i][0] )
            sY.append( hV[i][1] )
            sC.append( 'red' )
        else :
            rX.append( hV[i][0] )
            rY.append( hV[i][1] )
            rC.append( 'black' )

    '''
    # Adding vectors
    X = 0
    Y = 0
    j = 0
    vX = []
    vY = []
    U = []
    V = []
    for i in gV :
        dX = i[0] - X
        dY = i[1] - Y

        vX.append( X )
        vY.append( Y )
        U.append( dX )
        V.append( dY )
        #print(" i= " + str(i) + "( " + str( i[0]) + ", " + str(i[1]) + ")" )
        #plt.quiver( X, Y, dX, dY, angles='xy', scale_units='xy',scale=1, color= colorV[j] )
        X += dX
        Y += dY
        j += 1

    fig = ff.create_quiver(vX, vY, U, V )

    # adding retract points
    #aplt.scatter( sX, sY,s=20, c=sC, marker= '^')
    #plt.scatter( rX, rY,s=20, c=rC, marker= 'o')

    plt.iplot(fig)

