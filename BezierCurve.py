import scipy.special as scs
import matplotlib.pyplot as plt

class BezierCurve :

    def __init__(self, n ):

        self.n = n
        self.xs = []
        self.ys = []


    # Coefficient of Bezier Curve
    def b_nk(self, k,t):

        n = self.n
        bk = scs.comb(n,k)* pow(t,k)*(pow((1-t),(n-k)))
        return bk

    def ConstructCurve(self, nstep, plist = [] ):

        self.n = len( plist ) -1
        np = len( plist )
        print(" N = %d " %(np))

        xlist = []
        ylist = []
        for i in range( nstep+1 ) :
            t = i/nstep

            px = 0.
            py = 0.
            for j in range(np) :
                px = px + plist[j][0]*self.b_nk(j,t)
                py = py + plist[j][1]*self.b_nk(j,t)

            xlist.append( px )
            ylist.append( py )

        return [ xlist, ylist ]



    def QuadraticCurve(self, plist = []):

        self.n = 2
        p0 = plist[0]
        p1 = plist[1]
        p2 = plist[2]

        step = 50
        xlist = []
        ylist = []
        for i in range( step+1 ) :

            t = i/ step
            pxi = p0[0]*self.b_nk(0,t) + p1[0]*self.b_nk(1,t) + p2[0]*self.b_nk(2,t)
            pyi = p0[1]*self.b_nk(0,t) + p1[1]*self.b_nk(1,t) + p2[1]*self.b_nk(2,t)
            xlist.append( pxi )
            ylist.append( pyi )


        return [xlist, ylist ]



bc = BezierCurve(2)
plist   = [ [0,5], [0,0], [5,0] ]
bclist  = bc.QuadraticCurve( plist )

plist1  = [ [1,6], [8,1], [2,5], [1,1] ]
bclist1 = bc.ConstructCurve(50,plist1)

# setup cavas
fig = plt.figure( figsize=(7.5,7.5) )
fig.suptitle( 'Bezier Curve Demo', fontsize=10, fontweight='bold')

# one sub plot (x,y,index)
ax = fig.add_subplot(111)
ax.set_xlabel('x')
ax.set_ylabel('y')

# Plot XY limit and grid
plt.xlim([-5, 15])
plt.ylim([-5, 15])
plt.grid(b=True, which='major')


ax.plot( bclist[0], bclist[1], 'r.', lw=1 )
ax.plot( bclist1[0], bclist1[1], 'b.', lw=1 )

plt.show()
