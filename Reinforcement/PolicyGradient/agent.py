#!/usr/bin/env python
# coding=utf-8
'''
Author: John
Email: johnjim0816@gmail.com
Date: 2020-11-22 23:27:44
LastEditor: John
LastEditTime: 2020-11-23 17:04:37
Discription: 
Environment: 
'''

import torch
from torch.distributions import Bernoulli
from torch.autograd import Variable
import numpy as np

from model import FCN


class PolicyGradient:

    def __init__(self, state_dim, device='cpu', gamma=0.99, lr=0.01, batch_size=5):
        self.gamma = gamma
        self.policy_net = FCN(state_dim)
        self.optimizer = torch.optim.RMSprop(
            self.policy_net.parameters(), lr=lr)
        self.batch_size = batch_size

    def choose_action(self, state):
        state = torch.from_numpy(state).float()
        state = Variable(state)
        probs = self.policy_net(state)
        m = Bernoulli(probs)
        action = m.sample()

        action = action.data.numpy().astype(int)[0]  # 转为标量
        return action

    def update(self, reward_pool, state_pool, action_pool):
        # Discount reward
        running_add = 0 # 就是那个有discount的公式

        for i in reversed(range(len(reward_pool))): # 倒数
            if reward_pool[i] == 0:
                running_add = 0
            else:
                running_add = running_add * self.gamma + reward_pool[i]
                reward_pool[i] = running_add

        # 得到G

        # Normalize reward
        reward_mean = np.mean(reward_pool)
        reward_std = np.std(reward_pool)
        for i in range(len(reward_pool)):
            reward_pool[i] = (reward_pool[i] - reward_mean) / reward_std
        # 归一化

        # Gradient Desent
        self.optimizer.zero_grad()

        for i in range(len(reward_pool)): # 从前往后
            state = state_pool[i] 
            action = Variable(torch.FloatTensor([action_pool[i]]))
            reward = reward_pool[i]

            state = Variable(torch.from_numpy(state).float())
            probs = self.policy_net(state)
            m = Bernoulli(probs)
            # Negtive score function x reward
            loss = -m.log_prob(action) * reward # 核心
            # print(loss)
            loss.backward()

        self.optimizer.step()

    def save_model(self, path):
        torch.save(self.policy_net.state_dict(), path)

    def load_model(self, path):
        self.policy_net.load_state_dict(torch.load(path))
