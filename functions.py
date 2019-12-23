# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 13:25:46 2019

@author: ebaccourepbesaid
"""
import numpy as np
import math
import h5py
import pickle
import scipy.io
AWSstorageCost1=[0.025,0.025,0.025,0.025,0.024,0.024,0.0405,0.023,0.023,0.026]#First 50 TB / Month
AWSstorageCost2=[0.024,0.024,0.024,0.024,0.023,0.023,0.039,0.022,0.022,0.025]#Next 450 TB / Month
videoSize=0.738 # 0.738 Gbit 738Mbit for 1 hour, 2952Mbit for 4 Hours
PUTrequest=[0.000005,0.0000045,0.000005,0.000000589,0.0000054,0.0000053,0.000007,0.000005,0.000005,0.000005]#%per request
AWSmigartionCost=[0.086,0.08,0.09,0.09,0.02,0.02,0.16,0.02,0.02,0.02]# Per Gbit cost differ based on origin %China not available just assumption
GETrequest=[0.0000004,0.00000035,0.0000004,0.00000071,0.00000043,0.00000042,0.00000056,0.0000004,0.00000041,0.00000044]#per request
AWSservingRequestCost=[0.08,0.0108,0.08,0.134,0.05,0.05,0.19,0.05,0.05,0.05]#data transfer price from s3 to internet
# returns the vector containing allocation data from a fixed file
def getPredictedDataVec(key):
    mat=[]
    lines = open("data/outputFolder/" + key + ".csv", "r").read().splitlines()
    for line in lines[0:]:    
        temp=line.split(",")[0:]
        vec = []
        for i in temp:
            vec.append(float(i))
        mat.append(vec)
    return mat
def getDataVec(key):
    mat=[]
    lines = open("data/" + key + ".csv", "r").read().splitlines()
    for line in lines[0:]:    
        temp=line.split(",")[0:]
        vec = []
        for i in temp:
            vec.append(float(i))
        mat.append(vec)
    return mat
def getState(data, row): # We defined a function because we may add some feature engineering
    r=data[row]
    r=np.array(r)
    r=np.expand_dims(r,1)
    r=np.reshape(r,(1,11))
    return r 
def getDelay(key):
    mat=[]
    lines = open("data/" + key + ".csv", "r").read().splitlines()
    for line in lines[0:]:    
        temp=line.split(",")[0:]
        vec = []
        for i in temp:
            vec.append(float(i))
        mat.append(vec)
    return mat

def getReward(action,t,state):
        DelayMatrix=getDelay('DelayMatrix');
        delay=0
        nbViewers=0
        phy=0
        cost=0
        rho=0
        alpha=0
        theta=0
        beta=0
        zeta=0
        ac2=0
        lamda=0
        action=np.reshape(action, (10,11))
        action=np.round(action)
        # print(action)
        # print(state)
        #exit()
        state=state.tolist()[0]
        nbViewers=np.sum(state[1:11])
        for j in range(0,10):
            al=0
            # Cost of allocation in different sites
            cost=cost+action[j][0]*(AWSstorageCost1[j]*videoSize+PUTrequest[j])+action[j][0]*(AWSmigartionCost[int(state[0]-1)]*videoSize+GETrequest[int(state[0]-1)]) ####added action[j][0] on GETrequest
            for i in range(0,10):
                # Cost of serving from different sites
                cost=cost+state[i+1]*action[j][i+1]*(AWSservingRequestCost[i]*videoSize+GETrequest[i])
                delay=delay+state[i+1]*DelayMatrix[j][i]*action[j][i+1]
                #nbViewers=nbViewers+state[i+1]
                al=al+action[j][i+1]
                # If the number of viewers is 0 (state from 1 to 9), the whole column (i+1) elements in the action matrix should be equal to 0.
                if state[i+1]==0 and action[j][i+1]==1:
                    phy=phy-50
                    # if any element in the first column of the action matrix is 0, the whole line should be 0.
                if action[j][0]==0 and action[j][i+1]==1:
                    theta=theta-50
            # if any element in the first column is 1, at least one of elements in the same line should be 1 (This is not applied for the broadcaster server as it is allocated by default).
            if j != int(state[0]-1) and action[j][0]==1 and al==0:
                beta=beta-50
        avDelay=delay/nbViewers
        # the broadcaster action sould be 1: In the first line, the element action [broadcaster id] should be 1.
        if action[int(state[0]-1)][0]==0:
            zeta=-50
        else:
            zeta=20
            # the average delay should be bigger than 120.
        if avDelay>120:
            rho=-10
        else:
            rho=20

        
        for i in range(0,10):
            ac2=ac2+action[i][0]
        # at least there should be a one at the first column
        if ac2==0:
            lamda=-10
        for j in range(1,11):
            ac=0
            for i in range(0,10):
                ac=ac+action[i][j]   
            # in each action column (from 1 to 10), there should be only one 1. All zeros is permitted
            if ac>1:
                alpha=alpha-(40*ac)
             # if number of viewers in state [j] (state from 1 to 10) is not zero, the column j should contain a 1.
            if state[j]>0 and ac==0:
                    phy=phy-50
            if state[j]>0 and ac==1:
                phy=phy+20
            if state[j]==0 and ac==0:
                    phy=phy+80
        return np.reshape((-cost)+rho+phy+alpha+beta+zeta+lamda+theta,(1,))
def getActualReward(vid,state): # works for delay threshold 120.
        file="output"+str(vid+1)
        ar=getPredictedDataVec(file)
        cost=0
        phy=0
        state=state.tolist()[0]
        for j in range(0,10):
            cost=cost+ar[j][0]*(AWSstorageCost1[j]*videoSize+PUTrequest[j])+ar[j][0]*(AWSmigartionCost[int(state[0]-1)]*videoSize+GETrequest[int(state[0]-1)])
            for i in range(0,10):
                cost=cost+state[i+1]*ar[j][i+1]*(AWSservingRequestCost[i]*videoSize+GETrequest[i]) 
        for j in range(1,11):
            ac=0
            for i in range(0,10):
                ac=ac+ar[i][j]
            if state[j]==0 and ac==0:
                    phy=phy+10
        return np.reshape(20+20+phy-cost,(1,))    