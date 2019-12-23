
from stable_baselines.common.policies import MlpLstmPolicy,MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import PPO2
from stable_baselines.common.policies import FeedForwardPolicy, register_policy

from env.NetworkEnv import NetworkEnv
import pandas as pd
import numpy as np
import gym


class CustomPolicy(FeedForwardPolicy):
    def __init__(self, *args, **kwargs):
        super(CustomPolicy, self).__init__(*args, **kwargs,
                                           net_arch=[dict(pi=[400, 300, 128],
                                                          vf=[400, 200, 128])],
                                           feature_extraction="mlp")

# Register the policy, it will check that the name is not already taken
register_policy('CustomPolicy', CustomPolicy)

def main():


	env = SubprocVecEnv([lambda:  NetworkEnv() for i in range(100)])
	model = PPO2("CustomPolicy", env, verbose=0,gamma=0.2,cliprange_vf=-1)#)
	model = PPO2.load("NetworkModel",env=env)
	model.learn(total_timesteps=10000000)
	model.save("NetworkModel")
	#print("here")




if __name__ == "__main__":
	main()