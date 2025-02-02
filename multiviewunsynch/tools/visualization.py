# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import numpy as np
import cv2
from tools import util
import pickle
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def drawlines(img1,img2,lines,pts1,pts2):
    ''' 
    Function:
            draw lines and circles on image pair, specifically for epipolar lines
    Input:
            img1 = image on which we draw (epipolar) lines for the points in img2
            img2 = corresponding image
            lines = corresponding epipolar lines 
            pts1,pts2 = corresponding feature points
    Output:
            img1 = image1 with lines and circles
            img2 = image2 with circles 
    '''
    r,c = img1.shape

    # Convert grayscale to BGR if needed
    if len(img1.shape)==2:
        img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    if len(img2.shape)==2:
        img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)

    # Draw epipolar lines in image1 and corresponding feature points in both images
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2


def plotEpiline(img1, img2, pts1, pts2, F):
    '''
    Function:
            plot epipolar lines in both images, in form of N*2, type should be int
    Input:
            img1, img2 = image pair
            pts1, pts2 = corresponding feature points
            F = fundamental matrix
    Output:
            plot epipolar lines on image pair
    '''
    # Find epilines corresponding to points in right image (second image) and
    # drawing its lines on left image
    lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1,1,2), 2,F)
    lines1 = lines1.reshape(-1,3)
    img3 = drawlines(img1,img2,lines1,pts1,pts2)[0]

    # Find epilines corresponding to points in left image (first image) and
    # drawing its lines on right image
    lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
    lines2 = lines2.reshape(-1,3)
    img5 = drawlines(img2,img1,lines2,pts2,pts1)[0]

    # Show results
    cv2.namedWindow('Epipolar lines in img1',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Epipolar lines in img1',500,300)
    cv2.imshow('Epipolar lines in img1',img3)
    cv2.namedWindow('Epipolar lines in img2',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Epipolar lines in img2',500,300)
    cv2.imshow('Epipolar lines in img2',img5)
    cv2.waitKey(0)


def plot_epipolar_line(img1, img2, F, x1, x2):
    '''
    Plot epipolar lines of point correspondences.
    '''

    # pre-steps
    num = x1.shape[1]
    r1,c1 = img1.shape
    r2,c2 = img2.shape
    x1_coord = np.linspace(0,c1-1,100)
    x2_coord = np.linspace(0,c2-1,100)

    # Calculate epipolar lines
    line1 = np.dot(F,x1)
    line2 = np.dot(F.T,x2)

    # plot epipolar lines in img1, which are calculated using key points in img2
    plt.subplot(121),plt.imshow(img1,cmap='gray')
    for i in range(num):
        line = line2[:,i]
        y1_coord = np.array([(line[2]+line[0]*x)/(-line[1]) for x in x1_coord])
        idx = (y1_coord>=0) & (y1_coord<r1-1)
        plt.plot(x1_coord[idx],y1_coord[idx])
    plt.scatter(x1[0],x1[1])
    
    # plot epipolar lines in img2, which are calculated using key points in img1
    plt.subplot(122),plt.imshow(img2,cmap='gray')
    for i in range(num):
        line = line1[:,i]
        y2_coord = np.array([(line[2]+line[0]*x)/(-line[1]) for x in x2_coord])
        idx = (y2_coord>=0) & (y2_coord<r2-1)
        plt.plot(x2_coord[idx],y2_coord[idx])
    plt.scatter(x2[0],x2[1])

    plt.show()


def show_trajectory_2D(*x,title=None,color=True,line=False,text=False):
    plt.figure(figsize=(12, 10))
    num = len(x)
    for i in range(num):
        plt.subplot(1,num,i+1)
        plt.scatter(x[i][0],x[i][1],c=np.arange(x[i].shape[1])*color)
        if line:
            plt.plot(x[i][0],x[i][1])
        if text:
            for j in range(len(x[i][0])):
                plt.text(x[i][0,j], x[i][1,j], str(j), color='red',fontsize=12)

        # plt.gca().set_xlim([0,1920])
        # plt.gca().set_ylim([0,1080])

        plt.gca().invert_yaxis()
        plt.xlabel('X')
        plt.ylabel('Y')
    if title:
        plt.suptitle(title)
    plt.show()


def show_trajectory_3D(*X,title=None,color=True,line=False):
    fig = plt.figure(figsize=(12, 10))
    num = len(X)
    for i in range(num):
        ax = fig.add_subplot(1,num,i+1,projection='3d')
        
        if color:
            # ax.scatter3D(X[i][0],X[i][1],X[i][2],c='r')
            ax.scatter3D(X[i][0],X[i][1],X[i][2],c=np.arange(X[i].shape[1])*color)
        else:
            ax.scatter3D(X[i][0],X[i][1],X[i][2])

        if line:
            ax.plot(X[i][0],X[i][1],X[i][2])
        plt.xlabel('X')
        plt.ylabel('Y')
        # plt.xlim([-1.5, 1.5])
        # plt.ylim([-0.6, 1.0])
    if title:
        plt.suptitle(title)
    # plt.axis('off')
    plt.show()


def show_2D_all(*x,title=None,color=True,line=True,text=False):
    plt.figure(figsize=(12, 10))
    num = len(x)
    for i in range(num):
        # plt.subplot(1,num,i+1)

        c = ['r','b']
        plt.scatter(x[i][0],x[i][1],c=c[i])
        # plt.scatter(x[i][0],x[i][1],c=np.arange(x[i].shape[1])*color)
        if line:
            plt.plot(x[i][0],x[i][1])
        if text:
            for j in range(len(x[i][0])):
                plt.text(x[i][0,j], x[i][1,j], str(j), color='red',fontsize=12)

        # plt.gca().set_xlim([0,1920])
        # plt.gca().set_ylim([0,1080])
        # plt.gca().invert_yaxis()

        plt.xlabel('X')
        plt.ylabel('Y')
    if title:
        plt.suptitle(title)
    plt.show()


def show_3D_all(*X,title=None,color=True,line=True):
    fig = plt.figure(figsize=(20, 15))
    num = len(X)
    ax = fig.add_subplot(111,projection='3d')

    for i in range(num):
        if color:
            c = ['r','g']
            m = ['o','x']
            label = ['RTK ground truth', 'Reconstruction Spline']
            if i is 0:
                ax.scatter3D(X[i][0],X[i][1],X[i][2],s=60,c=c[i],marker='o',label=label[i])
            else:
                ax.scatter3D(X[i][0],X[i][1],X[i][2],s=60,c=c[i],marker=m[i],label=label[i])
                # ax.plot(X[i][0],X[i][1],X[i][2],c=c[i])

        else:
            ax.scatter3D(X[i][0],X[i][1],X[i][2])

        if line:
            ax.plot(X[i][0],X[i][1],X[i][2])
        plt.xlabel('X')
        plt.ylabel('Y')
    if title:
        plt.suptitle(title)
    
    ax.set_xlabel('East [m]',fontsize=20)
    ax.set_ylabel('North [m]',fontsize=20)
    ax.set_zlabel('Up [m]',fontsize=20)

    ax.view_init(elev=30,azim=-50)
    lgnd = ax.legend(loc=1, prop={'size': 30})
    for handle in lgnd.legendHandles:
        handle.set_sizes([100])
    # plt.axis('off')
    plt.show()


def show_spline(*spline,title=None):

    num = len(spline)
    for i in range(num):
        plt.subplot(1,num,i+1)
        x, y = spline[i][0], spline[i][1]
        plt.scatter(x[0],x[1],s=10,label='Origin')
        plt.plot(y[0],y[1],c='r',label='Spline interpolation')

        plt.gca().invert_yaxis()
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()

    if title:
        plt.suptitle(title)
    plt.show()


def error_hist(error,bins=None,title=None,label=None):

    assert len(error.shape)==1, 'Input must be a 1D array'

    if not bins:    bins = np.arange(0,70,5)
    if not title:   title = 'Error histogram [cm]'
    if not label:   label = 'Spline'

    plt.figure(figsize=(20, 15))
    plt.hist(error.T*100, bins, histtype='bar', color='b',label=label)
    plt.xticks(bins,fontsize=30)
    plt.yticks(fontsize=30)
    plt.legend(loc=1, prop={'size': 30})
    plt.title(title, fontsize=25)
    plt.show()


def error_traj(traj,error,thres=0.5,title=None,colormap='Wistia',size=100, text=None):

    assert len(error.shape)==1, 'Input must be a 1D array'
    assert traj.shape[0]==3, 'Input must be a 3D array'
    assert len(error)==traj.shape[1], 'Error must have the same shape as the trajectory'

    if not title:   title = 'Error over the trajectory [cm]'

    fig = plt.figure(figsize=(20, 15))
    plt.set_cmap(colormap)
    ax = fig.add_subplot(111,projection='3d')
    sc = ax.scatter3D(traj[0],traj[1],traj[2],c=error*100,marker='o',s=size)

    # Plot the timestamp of points that have large errors
    if text != None:
        assert len(text)==len(error), 'Wrong number of timestamps'
        text = text.astype(int)
        for i in range(len(text)):
            if error[i]>thres:
                ax.text(traj[0,i], traj[1,i], traj[2,i], str(text[i]), fontsize=5)

    ax.set_xlabel('East',fontsize=40,linespacing=100)
    ax.set_ylabel('North',fontsize=40,linespacing=3.2)
    ax.set_zlabel('Up',fontsize=40,linespacing=3.2)
    ax.view_init(elev=30,azim=-50)

    cbar = plt.colorbar(sc,fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=40)
    plt.title(title, fontsize=50)
    plt.show()


if __name__ == "__main__":
    # # Synthetic trajectory data
    # X = np.loadtxt('./data/Synthetic_Trajectory_generated.txt')
    # X_homo = np.insert(X,3,1,axis=0)
    
    # show_trajectory_3D(X,color=True)

    # # Fixposition data
    # X1 = np.loadtxt('./data/fixposition_1_kml.txt',delimiter=',')
    # X1 = X1.T

    # X2 = np.loadtxt('./data/fixposition_2_kml.txt',delimiter=',')
    # X2 = X2.T
    # show_trajectory_3D(X1,X2)

    # Triangulated real trajectory
    with open('./data/test_trajectory.pickle', 'rb') as file:
        results = pickle.load(file)

    for i in range(len(results['Beta'])):
        traj_1, traj_2 = results['X1'][i], results['X2'][i]
        show_trajectory_3D(traj_1,traj_2,
        title='Shift:{}, estimated beta:{:.3f}, without sync (left), with sync (right)'.format(
            results['shift'][i],results['Beta'][i],))

    fig,ax = plt.subplots(1,2,sharex=True)
    ax[0].plot(results['shift'],results['Beta'])
    ax[1].plot(results['shift'],np.asarray(results['Beta'])-np.asarray(results['shift']))
    ax[0].set_title('Estimation of Beta with different shifts')
    ax[1].set_title('Error of Beta with different shifts')
    ax[0].set_ylabel('Estimated Beta')
    ax[1].set_ylabel('Error of Beta')
    plt.xlabel('Shifts from -10 to 10')
    # fig.suptitle('Threshold 1 = {}, Threshold 2 = {}, Degree of spline = {}, Smooth factor = {}'.format(5,5,3,100))
    plt.show()

    print('finished')