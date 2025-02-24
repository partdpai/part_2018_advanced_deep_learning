'''
Cartpole balancing using a simple DQN with experience-replay.
'''

import numpy as np
import tensorflow as tf
import gym
import random
import copy
import math

env = gym.make("CartPole-v0")
render = True # set to True for rendering

num_episodes = 10000
batch_size = 64
memory_size = 200
H1 = 64
D = 4
learning_rate = 1e-2
gamma = 0.99
epsilon_max = 1.0
epsilon_min = 0.01

tf.reset_default_graph()
observations = tf.placeholder(tf.float32, [None,D], name="input_x")
W1 = tf.get_variable("W1", shape=[D, H1],
           initializer=tf.contrib.layers.xavier_initializer())
layer1 = tf.nn.relu(tf.matmul(observations,W1))

W2 = tf.get_variable("W2", shape=[H1, 2],
           initializer=tf.contrib.layers.xavier_initializer())

linear = tf.matmul(layer1, W2)
#Qout = tf.nn.sigmoid(linear)
Qout = linear
Qtarget = tf.placeholder(tf.float32, [None, 2], name="Qtarget")
#loglik = tf.log(Qtarget*(Qtarget - Qout) + (1 - Qtarget)*(Qtarget + Qout))
diffs = Qtarget - Qout
loss = -tf.reduce_mean(tf.square(diffs))
#loss = -tf.reduce_mean(loglik)
adam = tf.train.AdamOptimizer(learning_rate).minimize(loss)

init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)
    memory_states = []
    memory_targets = []
    for _ in xrange(num_episodes):
        observation = env.reset()
        done = False
        ep_states = []
        ep_targets = []
        memory_states_temp = []
        memory_targets_temp = []
        i = 0
        total_reward = 0
        while done == False:
            i += 1
            #print i
            state = np.reshape(observation, [1, D])
            #print state
            #ep_states.append(state)
            memory_states.append(state)
            #print memory_states
            Qvals = sess.run(Qout, feed_dict={observations: state})
            epsilon = epsilon_min + (epsilon_max - epsilon_min)*(math.exp(-0.01*_))
            if random.random() < epsilon:
                action = env.action_space.sample()
                #print "RANDOM"
            else:
                action = np.argmax(Qvals)
                #print "GREEDY"
            
            #take an e-greedy action
            new_state, reward, done, info = env.step(action)
            if render == True:
                env.render()

            total_reward += reward
            nextQvals = sess.run(Qout, feed_dict={observations: np.reshape(new_state,[1, D])})
            old_state = state
            observation = new_state
            maxQvals = np.max(nextQvals)
            if done == False:
                update = reward + (gamma*maxQvals)
                #print total_reward
            else:
                update = reward
            targetQvals = Qvals
            targetQvals[0, action] = update
            #ep_targets.append(targetQvals)
            memory_targets.append(targetQvals)

        memory_states_temp = copy.copy(memory_states)
        memory_targets_temp = copy.copy(memory_targets)

        memory_states_temp = np.vstack(memory_states_temp)
        memory_targets_temp = np.vstack(memory_targets_temp)

        temp_list = zip(memory_states_temp, memory_targets_temp)
        random.shuffle(temp_list)
        ep_states, ep_targets = zip(*temp_list[:batch_size])
        sess.run(adam, feed_dict={observations: ep_states, Qtarget: ep_targets})
        if _ % memory_size == 0:
            memory_states = []
            memory_targets = []
        print ("reward this episode :" + total_reward)






