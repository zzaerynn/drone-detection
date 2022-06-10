import pickle
#serialization or flattening 
import numpy as np
import simplekml

kml = simplekml.Kml()

with open('result_dataset4.pkl', 'rb') as f:
    data = pickle.load(f)

trajectory = data.traj
x,y,z = trajectory[1], trajectory[2], trajectory[3]

num= len(x)
numberofnewpoint =int(num/6)
j=0
div=2500
for i in range(0, num, numberofnewpoint):
    nx=(127.13+round(x[i],7)/div)
    ny=(35.84+round(y[i],7)/div)
    nz=(40+round(z[i],7))
    # nz=(40+z[i])
    nn="point {0}" .format(j)
    j=j+1
#     kml.newpoint(name=nn, coords=[(nx,ny,nz)])
    pnt=kml.newpoint(name=nn, coords=[(nx,ny,nz)])
    pnt.style.labelstyle.color = simplekml.Color.red  
    pnt.altitudemode = simplekml.AltitudeMode.absolute
    pnt.style.labelstyle.scale = 2  
    pnt.style.iconstyle.icon.href

points = []
for i in range(len(x)):
    nx=(127.13+round(x[i],7)/div)
    ny=(35.84+round(y[i],7)/div)
#     nz=(40+round(z[i],7))
    nz=(40+z[i])
    coord= (nx,ny,nz)
    points.append(coord)

ls=kml.newlinestring(name="Pathway")
ls.coords = points
ls.extrude = 1
ls.altitudemode = simplekml.AltitudeMode.absolute
ls.style.linestyle.width = 5
ls.style.linestyle.color = simplekml.Color.blue  

kml.save("result_dataset4.kml")