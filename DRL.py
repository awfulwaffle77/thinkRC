# DEEP REINFORCEMENT LEARNING Module

from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
import random
import numpy as np
import pandas as pd
from operator import add
import collections


class DRLAgent(object):
    def __init__(self, params):
        self.reward = 0
        self.gamma = params['discount_factor']  # discount rate
        self.dataframe = pd.DataFrame()
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = params['learning_rate']
        self.epsilon = 1
        self.actual = []
        self.first_layer = params['first_layer_size']
        self.second_layer = params['second_layer_size']
        self.third_layer = params['third_layer_size']
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.weights = params['weights_path']
        self.load_weights = params['load_weights']
        self.model = self.network()

    def network(self):
        model = Sequential()
        model.add(Dense(units=self.first_layer, activation='relu', input_dim=3))
        model.add(Dense(units=self.second_layer, activation='relu'))
        model.add(Dense(units=self.third_layer, activation='relu'))
        model.add(Dense(units=3, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if self.load_weights:
            model.load_weights(self.weights)
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory, batch_size):
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                #target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
                target = np.amax(self.model.predict(np.array([state]))[0]) + self.learning_rate *\
                         (reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
                          - np.amax(self.model.predict(np.array([state]))[0]))
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

    def train_short_memory(self, state, action, reward, next_state, done):
        target = reward
        if not done:
            next_state = np.reshape(next_state, (1, 3))
            reshaped_state = np.reshape(state, (1, 3))
            #target = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            target = np.amax(self.model.predict(reshaped_state)[0]) + self.learning_rate * \
                     (reward + self.gamma * np.amax(self.model.predict(next_state)[0])
                      - np.amax(self.model.predict(reshaped_state)[0]))
        target_f = self.model.predict(np.reshape(state, (1, 3)))
        target_f[0] = 0
        target_f[0][np.argmax(action)] = target
        self.model.fit(np.reshape(state, (1, 3)), target_f, epochs=1, verbose=0)
