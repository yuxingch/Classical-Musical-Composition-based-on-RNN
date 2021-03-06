from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf

class RnnModel:
    
    def __init__(self, placeholder, min_step=10, state_dim=128):
        self.min_step = min_step
        self.state_dim = state_dim
        self.rnn_cell = tf.contrib.rnn.BasicLSTMCell(state_dim)
        # Initial state of the LSTM memory.
        self.music_input = placeholder['music_input']
        self.batch_size = tf.shape(self.music_input)[0]
        self.time_range = tf.shape(self.music_input)[1]
        self.note_input_dim = tf.shape(self.music_input)[2]
        self.targets_pitch = self.music_input[:,-1,:]
        self.initial_state = self.rnn_cell.zero_state(self.batch_size, dtype=tf.float32)
        self.build()
        self.loss()
        
        self.optimizer = tf.train.AdamOptimizer(learning_rate=0.1)
        self.grads_and_vars = self.optimizer.compute_gradients(self.loss)
        clipped_grads_and_vars = [(tf.clip_by_value(grad, -5.0, 5.0) if grad is not None else None, var) 
                for grad, var in self.grads_and_vars]
        self.grad, _ = clipped_grads_and_vars[1]
        for _, var in clipped_grads_and_vars:
            print(var.name)
        self.train_op = self.optimizer.apply_gradients(clipped_grads_and_vars)

    def build(self):

        self.embeddings = tf.get_variable('note_embedding', shape=(self.state_dim, self.state_dim),
                                                 dtype=tf.float32, 
                                                 initializer=tf.contrib.layers.xavier_initializer())

        music_input_reshaped = tf.reshape(self.music_input, [self.batch_size * self.time_range, self.state_dim])
        self.music_input = tf.matmul(music_input_reshaped, self.embeddings)
        self.music_input = tf.reshape(self.music_input, [self.batch_size, self.time_range, self.state_dim])

        # The value of state is updated after processing each batch of notes.
        # The LSTM output can be used to make next pitch predictions
        self.outputs, state = tf.nn.dynamic_rnn(self.rnn_cell, self.music_input[:, :-1, :],
                                      initial_state=self.initial_state,
                                      dtype=tf.float32)
                                      
        
        # self.vars = {}
        # prev_vec = tf.reshape(self.music_input[:, -2, :], [self.batch_size, self.note_input_dim])
        # self.vars['weights'] = tf.get_variable('weights', shape=(self.state_dim, self.state_dim),
        #                                         dtype=tf.float32, 
        #                                         initializer=tf.contrib.layers.xavier_initializer())
        # self.vars['bias'] = tf.get_variable('bias', shape=[self.state_dim], dtype=tf.float32,
        #                                     initializer=tf.constant_initializer(0.0))
        # outputs = tf.matmul(prev_vec, self.vars['weights']) + self.vars['bias']
         
        # output_trunc = outputs[:-min_step, :]
        # output_flattened = tf.reshape(output_truc, shape=[self.batch_size, 
        #                                                  tf.shape(output_trunc)[1] *
        #                                                  tf.shape(output_truct)[2]],
        #                              name='flatten_output')

        #W = tf.get_variable(name='weight',shape=(,128),dtype=tf.float32)
        #b = tf.get_variable(name='bias',shape=128,dtype=tf.float32)
        #logit = tf.matmul(outputs, W) + b 
        #prob= tf.nn.softmax(self.outputs) 
        prob = tf.nn.sigmoid(self.outputs)
        self.pred = prob[:, -1, :]
        # self.pred = prob


    def loss(self):
        #target_flattened = tf.reshape(self.targets_pitch, 
        #                              [self.batch_size, (self.time_range-self.min_step)*self.note_input_dim], 'reshape_target')
        #pred_flattened = tf.reshape(self.pred,
        #                            [self.batch_size, (self.time_range-self.min_step)*self.note_input_dim], 'reshape_pred')

        # compute cost
        
        loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.targets_pitch, logits=self.pred) 
        self.loss = tf.reduce_mean(loss)
        #self.loss = tf.nn.l2_loss(self.targets_pitch - self.pred)
        tf.summary.scalar('loss', self.loss)

        
        
        #compute accuracy
        #correct_pred = tf.equal(tf.argmax(pred_flattened,1), tf.argmax(target_flattened,1))
        #self.accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
