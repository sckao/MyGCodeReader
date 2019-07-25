import numpy as np
from stl import mesh
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt


stl_fname = input(' STL FileName : ')
theMesh = mesh.Mesh.from_file( stl_fname )

#vtx_count = 6
#data = numpy.zeros( vtx_count, dtype= mesh.Mesh.dtype )
#theMesh = mesh.Mesh( data, remove_empty_areas= False)

#theMesh.normals


fig = plt.figure()
axes = mplot3d.Axes3D( fig )
axes.add_collection3d( mplot3d.art3d.Poly3DCollection(theMesh.vectors) )

scale = theMesh.points.flatten(-1)
axes.auto_scale_xyz(scale,scale,scale)

plt.show()
