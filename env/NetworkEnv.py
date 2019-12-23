import random
import json
import gym
from gym import spaces
import pandas as pd
import numpy as np
from functions import * 
from sklearn.preprocessing import MinMaxScaler


class NetworkEnv(gym.Env):

    metadata = {'render.modes': ['human']}
    def __init__(self):
        super(NetworkEnv, self).__init__()

        self.action_space = spaces.MultiBinary(110)

            # Prices contains the OHCL values for the last five prices
        self.observation_space = spaces.Box(
                low=0, high=1.0, shape=(1,11), dtype=np.float32)


        allocation_name='data'#data #Complete

        self.data = getDataVec(allocation_name)
        self.originalData=getDataVec(allocation_name)


        self.maxnumber=np.amax(self.originalData)

        #between 0 and 1 now
        self.data=self.data/self.maxnumber


        self.current_step = 0
        self.episode_reward=0
        self.episode=0

    def _next_observation(self):

        self.cur_state = getState(self.data,self.current_step)




        return self.cur_state



    def _take_action(self, action):
        state=getState(self.originalData,self.current_step)[0]

        #print(state)
        #print(action)
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



        for j in range(0,10):
            counternum=0
            for i in range(0,10):
                # If the number of viewers is 0 (state from 1 to 9), the whole column (i+1) elements in the action matrix should be equal to 0.
                if state[j+1]==0 and action[i][j+1]==1: ###CORRECTED THIS
                            counternum=counternum+1
                            phy=phy-100
            if(counternum==0):
                phy=phy+100


        ##Each column must have one and only one entry . because each region must be served by only server
        for j in range(0,10):
            counternum=0
            for i in range(0,10):
                if state[j+1]>=1 and action[i][j+1]==1: 
                    counternum=counternum+1
            if(counternum==1):
                phy=phy+100
            if(counternum>1):
                phy=phy-(50*counternum)
            if(state[j+1]>=1 and counternum == 0):
                phy=phy-50





        # for j in range(0,10):
        #     for i in range(0,10):

        #         # if any element in the first column of the action matrix is 0, the whole line should be 0.
        #         if action[j][0]==0 and action[j][i+1]==1:
        #                     theta=theta-50


        # for j in range(0,9):
        #     SameColumnCounter=0
        #     for i in range(0,11):

        #         if(i=0): ###because this means wether to broadcast to user from this server or not
        #             continue

        #         if (action[j][i])







        if action[int(state[0]-1)][0]==0:
            zeta=-50
        else:
            zeta=20

        
        self.rewards=zeta+theta+phy



    def step(self, action):
        action=np.reshape(action, (10,11))
        self.action=action

        
        self._take_action(action)
        reward=self.rewards
        self.episode_reward=self.episode_reward+reward

        ####once end of step
        #self.reset()

        self.render("human")

        self.current_step=self.current_step+1

        done=False
        if(self.current_step>=len(self.originalData)):
            #self.reset()
            done=True
            self.current_step=0


        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
        self.episode=self.episode+1

        self.current_step = 0

        print("Episode number:  "+str(self.episode)+":  Total Episode Reward:  :"+str(self.episode_reward))
        self.episode_reward = 0
        return self._next_observation()



    def render(self, mode='human'):
       
        if(self.current_step==0):
            print(str(self.current_step)+": "+str(self.rewards))
            print(self.action)
            print("------------")