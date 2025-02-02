# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np
import pickle
from tools import visualization as vis
from datetime import datetime
from reconstruction import common
from analysis.compare_gt import align_gt
import sys
import cv2

if len(sys.argv) < 2:
    print( "Please provide a path to a proper config file")
    sys.exit()

# Initialize a scene from the json template
flight = common.create_scene(sys.argv[1])

# Truncate detections
flight.cut_detection(second=flight.settings['cut_detection_second'])

# Add prior alpha
flight.init_alpha()

# Compute time shift for each camera
flight.time_shift()

# Convert raw detections into the global timeline
flight.detection_to_global()

# Initialize the first 3D trajectory
flight.init_traj(error=flight.settings['thres_Fmatix'])

# Convert discrete trajectory to spline representation
flight.traj_to_spline(smooth_factor=flight.settings['smooth_factor'])


'''---------------Incremental reconstruction----------------'''
start = datetime.now()
np.set_printoptions(precision=4)

cam_temp = 2
while True:
    print('\n----------------- Bundle Adjustment with {} cameras -----------------'.format(cam_temp))
    print('\nMean error of each camera before BA:   ', np.asarray([np.mean(flight.error_cam(x)) for x in flight.sequence[:cam_temp]]))

    # Bundle adjustment
    res = flight.BA(cam_temp, rs=flight.settings['rolling_shutter'],\
        motion_reg=flight.settings['motion_reg'],\
        motion_weights=flight.settings['motion_weights'],\
        rs_bounds=flight.settings['rs_bounds'])

    print('\nMean error of each camera after first BA:    ', np.asarray([np.mean(flight.error_cam(x)) for x in flight.sequence[:cam_temp]]))
    
    flight.remove_outliers(flight.sequence[:cam_temp],thres=flight.settings['thres_outlier'])

    # Bundle adjustment after outlier removal
    res = flight.BA(cam_temp, rs=flight.settings['rolling_shutter'],\
        motion_reg=flight.settings['motion_reg'],\
        motion_weights=flight.settings['motion_weights'],\
        rs_bounds=flight.settings['rs_bounds'])

    print('\nMean error of each camera after second BA:    ', np.asarray([np.mean(flight.error_cam(x)) for x in flight.sequence[:cam_temp]]))
    
    num_end = flight.numCam if flight.find_order else len(flight.sequence)
    if cam_temp == num_end:
        print('\nTotal time: {}\n\n\n'.format(datetime.now()-start))
        break
    
    # Select the next camera if not pre-defined
    flight.select_most_overlap()

    # Add the next camera and get its pose
    flight.get_camera_pose(flight.sequence[cam_temp])

    # Triangulate new points and update the 3D spline
    flight.triangulate(flight.sequence[cam_temp], flight.sequence[:cam_temp], thres=flight.settings['thres_triangulation'],
                       factor_t2s=flight.settings['smooth_factor'], factor_s2t=flight.settings['sampling_rate'])

    print('\nTotal time: {}\n\n\n'.format(datetime.now()-start))
    cam_temp += 1
    flight.traj_len = []

flight.spline_to_traj(sampling_rate=1)

#kalman filter applying
kf = cv2.KalmanFilter(dynamParams = 3, measureParams=3)
#B
kf.controlMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32)
#H
kf.measurementMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) 
#R
kf.measurementNoiseCov = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32)  * 2.5
#Q
kf.processNoiseCov = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) *0.1
#A
kf.transitionMatrix = np.array([[1,0,0], [0,1,0], [0,0,1]], np.float32) 
# 
def predict(x, y, z):
    measured = np.array([[np.float32(x)], [np.float32(y)], [np.float32(z)]])
    kf.correct(measured)
    predicted = kf.predict()
    x,y,z = predicted[0],predicted[1], predicted[2]
    return x,y,z

trajectory = flight.traj
x,y,z = trajectory[1], trajectory[2], trajectory[3]

for i in range(len(flight.traj[1])):
    predx,predy,predz = predict(x[i],y[i],z[i])
    x = np.append(x, predx)
    y = np.append(y, predy)
    z = np.append(z, predz)

traj = np.array([x,y,z], np.float32)
# flight.traj[1:] = np.array([x,y,z], np.float32)

# flight.traj = np.array([flight.traj[0],x,y,z], np.float32)


# Visualize the 3D trajectory
vis.show_trajectory_3D(traj,line=False)
flight.out  = {'reconst_tran' : flight.traj[1:]}
# Align with the ground truth data if available
if flight.gt:
    flight.out = align_gt(flight, flight.gt['frequency'], flight.gt['filepath'], visualize=False)

with open(flight.settings['path_output'],'wb') as f:
    pickle.dump(flight, f)


print('Finished!')