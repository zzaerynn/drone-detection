import pickle
#serialization or flattening 
import numpy as np
import simplekml
from tools import visualization as vis
import cv2

kml = simplekml.Kml()

with open('result_dataset4.pkl', 'rb') as f:
    data = pickle.load(f)

trajectory = data.traj
x,y,z = trajectory[1], trajectory[2], trajectory[3]

# vis.show_trajectory_3D(data.traj[1:],line=False)

kf = cv2.KalmanFilter(dynamParams = 3, measureParams=3)
kf.controlMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) #B
kf.measurementMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) #H
kf.measurementNoiseCov = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) * 2.5 #R
kf.processNoiseCov = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) *0.1 #Q
kf.transitionMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) #A

def predict(x, y, z):
    measured = np.array([[np.float32(x)], [np.float32(y)], [np.float32(z)]])
    kf.correct(measured)
    predicted = kf.predict()
    x,y,z = predicted[0],predicted[1], predicted[2]
    return x,y,z

for i in range(len(x)):
    predx,predy,predz = predict(x[i],y[i],z[i])
    x = np.append(x, predx)
    y = np.append(y, predy)
    z = np.append(z, predz)

predTraj = np.array([x,y,z], np.float32)

vis.show_trajectory_3D(predTraj,line=False)

newpt =int(len(x)/6)
j=0
div=2500

for i in range(0, len(x), newpt):
    nx=(127.13+round(x[i],7)/div)
    ny=(35.84+round(y[i],7)/div)
    nz=(40+round(z[i],7))
    # nz=(40+z[i])
    nn="cam location {0}" .format(j)
    j=j+1
#     kml.newpoint(name=nn, coords=[(nx,ny,nz)])
    pnt=kml.newpoint(name=nn, coords=[(nx,ny,nz)])
    pnt.style.labelstyle.color = simplekml.Color.red  
    pnt.altitudemode = simplekml.AltitudeMode.absolute
    pnt.style.labelstyle.scale = 1
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