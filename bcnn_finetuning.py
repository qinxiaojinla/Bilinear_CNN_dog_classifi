from __future__ import print_function
import tensorflow as tf
import numpy as np
import os
from utils.data_loader import data_loader_
from utils.utils_ import touch_dir

import random
import time




def random_flip_right_to_left(image_batch):
    '''
    This function will flip the images randomly.
    Input: batch of images [batch, height, width, channels]
    Output: batch of images flipped randomly [batch, height, width, channels]
    '''
    result = []
    for n in range(image_batch.shape[0]):
        if bool(random.getrandbits(1)):     ## With 0.5 probability flip the image
            result.append(image_batch[n][:,::-1,:])
        else:
            result.append(image_batch[n])
    return result



class vgg16:
    def __init__(self, imgs, weights=None, sess=None):
        self.imgs = imgs
        self.last_layer_parameters = []     ## Parameters in this list will be optimized when only last layer is being trained 
        self.parameters = []                ## Parameters in this list will be optimized when whole BCNN network is finetuned
        self.convlayers()                   ## Create Convolutional layers
        self.fc_layers()                    ## Create Fully connected layer
        self.weight_file = weights          


    def convlayers(self):
        
        # zero-mean input
        with tf.name_scope('preprocess') as scope:
            mean = tf.constant([110.61220668946963, 127.15494646868024, 135.13440353131017], dtype=tf.float32, shape=[1, 1, 1, 3], name='img_mean')
            images = self.imgs-mean
            print('Adding Data Augmentation')


        # conv1_1
        with tf.variable_scope("conv1_1"):
            weights = tf.get_variable("W", [3,3,3,64], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [64], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(images, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv1_1 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # conv1_2
        with tf.variable_scope("conv1_2"):
            weights = tf.get_variable("W", [3,3,64,64], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [64], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv1_1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv1_2 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]

        # pool1
        self.pool1 = tf.nn.max_pool(self.conv1_2,
                               ksize=[1, 2, 2, 1],
                               strides=[1, 2, 2, 1],
                               padding='SAME',
                               name='pool1')

        # conv2_1
        with tf.variable_scope("conv2_1"):
            weights = tf.get_variable("W", [3,3,64,128], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [128], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.pool1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv2_1 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]



        # conv2_2
        with tf.variable_scope("conv2_2"):
            weights = tf.get_variable("W", [3,3,128,128], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [128], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv2_1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv2_2 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # pool2
        self.pool2 = tf.nn.max_pool(self.conv2_2,
                               ksize=[1, 2, 2, 1],
                               strides=[1, 2, 2, 1],
                               padding='SAME',
                               name='pool2')

        # conv3_1
        with tf.variable_scope("conv3_1"):
            weights = tf.get_variable("W", [3,3,128,256], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [256], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.pool2, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv3_1 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # conv3_2
        with tf.variable_scope("conv3_2"):
            weights = tf.get_variable("W", [3,3,256,256], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [256], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv3_1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv3_2 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]

        # conv3_3
        with tf.variable_scope("conv3_3"):
            weights = tf.get_variable("W", [3,3,256,256], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [256], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv3_2, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv3_3 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # pool3
        self.pool3 = tf.nn.max_pool(self.conv3_3,
                               ksize=[1, 2, 2, 1],
                               strides=[1, 2, 2, 1],
                               padding='SAME',
                               name='pool3')

        # conv4_1
        with tf.variable_scope("conv4_1"):
            weights = tf.get_variable("W", [3,3,256,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.pool3, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv4_1 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # conv4_2
        with tf.variable_scope("conv4_2"):
            weights = tf.get_variable("W", [3,3,512,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv4_1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv4_2 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # conv4_3
        with tf.variable_scope("conv4_3"):
            weights = tf.get_variable("W", [3,3,512,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv4_2, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv4_3 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]

        # pool4
        self.pool4 = tf.nn.max_pool(self.conv4_3,
                               ksize=[1, 2, 2, 1],
                               strides=[1, 2, 2, 1],
                               padding='SAME',
                               name='pool4')

        # conv5_1
        with tf.variable_scope("conv5_1"):
            weights = tf.get_variable("W", [3,3,512,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.pool4, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv5_1 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]


        # conv5_2
        with tf.variable_scope("conv5_2"):
            weights = tf.get_variable("W", [3,3,512,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv5_1, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv5_2 = tf.nn.relu(conv + biases)
            self.parameters += [weights, biases]
            

        # conv5_3
        with tf.variable_scope("conv5_3"):
            weights = tf.get_variable("W", [3,3,512,512], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
             # Create variable named "biases".
            biases = tf.get_variable("b", [512], initializer=tf.constant_initializer(0.1), trainable=True)
            conv = tf.nn.conv2d(self.conv5_2, weights, strides=[1, 1, 1, 1], padding='SAME')
            self.conv5_3 = tf.nn.relu(conv + biases)

            self.parameters += [weights, biases]
            self.special_parameters = [weights,biases]

        ''' Reshape conv5_3 from [batch_size, height, width, number_of_filters]
           to [batch_size, number_of_filters, height, width]'''
        self.conv5_3 = tf.transpose(self.conv5_3, perm=[0,3,1,2])


        ''' Reshape conv5_3 from [batch_size, number_of_filters, height*width] '''
        self.conv5_3 = tf.reshape(self.conv5_3,[-1,512,784])

        ''' A temporary variable which holds the transpose of conv5_3 '''
        conv5_3_T = tf.transpose(self.conv5_3, perm=[0,2,1])

        '''Matrix multiplication [batch_size,512,784] x [batch_size,784,512] '''
        self.phi_I = tf.matmul(self.conv5_3, conv5_3_T)

        '''Reshape from [batch_size,512,512] to [batch_size, 512*512] '''
        self.phi_I = tf.reshape(self.phi_I,[-1,512*512])
        print('Shape of phi_I after reshape', self.phi_I.get_shape())

        self.phi_I = tf.divide(self.phi_I,784.0)  
        print('Shape of phi_I after division', self.phi_I.get_shape())

        '''Take signed square root of phi_I'''
        self.y_ssqrt = tf.multiply(tf.sign(self.phi_I),tf.sqrt(tf.abs(self.phi_I)+1e-12))
        print('Shape of y_ssqrt', self.y_ssqrt.get_shape())

        '''Apply l2 normalization'''
        self.z_l2 = tf.nn.l2_normalize(self.y_ssqrt, dim=1)
        print('Shape of z_l2', self.z_l2.get_shape())




    def fc_layers(self):

        with tf.variable_scope('fc-new') as scope:
            fc3w = tf.get_variable('W', [512*512, 100], initializer=tf.contrib.layers.xavier_initializer(), trainable=True)
            #fc3b = tf.Variable(tf.constant(1.0, shape=[100], dtype=tf.float32), name='biases', trainable=True)
            fc3b = tf.get_variable("b", [100], initializer=tf.constant_initializer(0.1), trainable=True)
            self.fc3l = tf.nn.bias_add(tf.matmul(self.z_l2, fc3w), fc3b)
            self.last_layer_parameters += [fc3w, fc3b]

    def load_initial_weights(self, session):

        '''weight_dict contains weigths of VGG16 layers'''
        weights_dict = np.load(self.weight_file, encoding = 'bytes')

        
        '''Loop over all layer names stored in the weights dict
           Load only conv-layers. Skip fc-layers in VGG16'''
        vgg_layers = ['conv1_1','conv1_2','conv2_1','conv2_2','conv3_1','conv3_2','conv3_3','conv4_1','conv4_2','conv4_3','conv5_1','conv5_2','conv5_3']
        
        for op_name in vgg_layers:
            with tf.variable_scope(op_name, reuse = True):
                
              # Loop over list of weights/biases and assign them to their corresponding tf variable
                # Biases
              
              var = tf.get_variable('b', trainable = True)
              print('Adding weights to',var.name)
              session.run(var.assign(weights_dict[op_name+'_b']))
                  
            # Weights
              var = tf.get_variable('W', trainable = True)
              print('Adding weights to',var.name)
              session.run(var.assign(weights_dict[op_name+'_W']))

        with tf.variable_scope('fc-new', reuse = True):
            '''
            Load fc-layer weights trained in the first step. 
            Use file .py to train last layer
            '''
            last_layer_weights = np.load('last_layers_epoch_15_448.npz')
            print('Last layer weights: last_layers_epoch_10_1.npz')
            var = tf.get_variable('W', trainable = True)
            print('Adding weights to',var.name)
            session.run(var.assign(last_layer_weights['arr_0'][0]))

            var = tf.get_variable('b', trainable = True)
            print('Adding weights to',var.name)
            session.run(var.assign(last_layer_weights['arr_0'][1]))



if __name__ == '__main__':

    # '''
    # Load Training and Validation Data
    # '''
    # # train_data = h5py.File('../new_train.h5', 'r')
    # val_data = h5py.File('./new_val_224.h5', 'r')
    #
    # print('Input data read complete')
    #
    # # X_train, Y_train = train_data['X'], train_data['Y']
    # X_val, Y_val = val_data['X'], val_data['Y']
    # print("Data shapes -- (val)", X_val.shape, Y_val.shape)
    #
    # '''Shuffle the data'''
    # # X_train, Y_train = shuffle(X_train, Y_train)
    # X_val, Y_val = shuffle(X_val, Y_val)
    # print("Data shapes -- ( val)", X_val.shape, X_val.shape)
    data_l = data_loader_(batch_size=8,proportion=0.85,shuffle=True,data_add=2,onehot=True,data_size=448,nb_classes=100)
    
    
    sess = tf.Session()     ## Start session to create training graph

    imgs = tf.placeholder(tf.float32, [None, 448, 448, 3])
    target = tf.placeholder("float", [None, 100])

    #print 'Creating graph'
    vgg = vgg16(imgs, 'vgg16_weights.npz', sess)

    
    print('VGG network created')
    

    # Defining other ops using Tensorflow
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=vgg.fc3l, labels=target))


    print([_.name for _ in vgg.parameters])


    optimizer = tf.train.MomentumOptimizer(learning_rate=0.0003, momentum=0.9).minimize(loss)
    
    check_op = tf.add_check_numerics_ops()


    correct_prediction = tf.equal(tf.argmax(vgg.fc3l,1), tf.argmax(target,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    num_correct_preds = tf.reduce_sum(tf.cast(correct_prediction, tf.float32))

    sess.run(tf.global_variables_initializer())

    saver = tf.train.Saver()
    vgg.load_initial_weights(sess)
    print([_.name for _ in vgg.parameters])

    
    batch_size = 16

    for v in tf.trainable_variables():
        print("Trainable variables", v)
    print('Starting training')

    lr = 0.00001
    finetune_step = -1

    val_batch_size = data_l.batch_szie
    total_val_count = data_l.test_length
    correct_val_count = 0.0
    val_loss = 0.0
    total_val_batch = int(total_val_count/val_batch_size)

    for i in range(total_val_batch):
        batch_val_x, batch_val_y = data_l.get_test_data()
        print (batch_val_x.shape)
        print (batch_val_y.shape)
        val_loss += sess.run(loss, feed_dict={imgs: batch_val_x, target: batch_val_y})

        pred = sess.run(num_correct_preds, feed_dict = {imgs: batch_val_x, target: batch_val_y})
        correct_val_count+=pred

    print("##############################")
    print("Validation Loss -->", val_loss)
    print("correct_val_count, total_val_count", correct_val_count, total_val_count)
    print("Validation Data Accuracy -->", 100.0*correct_val_count/(1.0*total_val_count))
    print("##############################")

    checkpoint_path = os.path.join(os.getcwd(), 'model' )
    touch_dir(checkpoint_path)
    checkpoint_path = os.path.join(checkpoint_path, 'model.ckpt')
    saver.save(sess, checkpoint_path)
    print("saved to " + checkpoint_path)
    validation_accuracy_buffer = []
    for epoch in range(100):
        avg_cost = 0.

        total_test_count = data_l.train_length/(data_l.batch_szie/data_l.data_add)
        for i in range(total_test_count):
            batch_xs, batch_ys = data_l.get_train_data()
            print (batch_xs.shape)
            print (batch_ys.shape)
            start = time.time()
            sess.run([optimizer,check_op], feed_dict={imgs: batch_xs, target: batch_ys})
            if i%20==0:
                print('Full BCNN finetuning, time to run optimizer for batch size 32:',time.time()-start,'seconds')


            cost = sess.run(loss, feed_dict={imgs: batch_xs, target: batch_ys})
            avg_cost +=cost
            if i % 20 == 0:
                print ('Learning rate: ', (str(lr)))
                if epoch <= finetune_step:
                    print("Training last layer of BCNN_DD")
                else:
                    print("Fine tuning all BCNN_DD")

                print("Epoch:", '%03d' % (epoch+1), "Step:", '%03d' % i ,"Loss:", str(cost))
                print("Epoch:", '%03d' % (epoch + 1), "Step:", '%03d' % i, "AVG_Loss:", str(avg_cost/(i+1)))
                print("Training Accuracy -->", accuracy.eval(feed_dict={imgs: batch_xs, target: batch_ys}, session=sess))
                #print(sess.run(vgg.fc3l, feed_dict={imgs: batch_xs, target: batch_ys}))


        val_batch_size = data_l.batch_szie
        total_val_count = data_l.test_length
        correct_val_count = 0.0
        val_loss = 0.0
        total_val_batch = int(total_val_count / val_batch_size)

        for j in range(total_val_batch):
            batch_val_x, batch_val_y = data_l.get_test_data()
            print(batch_val_x.shape)
            print(batch_val_y.shape)
            val_loss += sess.run(loss, feed_dict={imgs: batch_val_x, target: batch_val_y})

            pred = sess.run(num_correct_preds, feed_dict={imgs: batch_val_x, target: batch_val_y})
            correct_val_count += pred

        print("##############################")
        print("Validation Loss -->", val_loss)
        print("correct_val_count, total_val_count", correct_val_count, total_val_count)
        print("Validation Data Accuracy -->", 100.0 * correct_val_count / (1.0 * total_val_count))
        print("##############################")

        checkpoint_path = os.path.join(os.getcwd(), 'model_tf%s' % str(epoch))
        touch_dir(checkpoint_path)
        checkpoint_path = os.path.join(checkpoint_path, 'model.ckpt')
        saver.save(sess, checkpoint_path)
        print("saved to " + checkpoint_path)


        if epoch>40:

            validation_accuracy_buffer.append(100.0*correct_val_count/(1.0*total_val_count))
            ## Check if the validation accuracy has stopped increasing
            if len(validation_accuracy_buffer)>10:
                index_of_max_val_acc = np.argmax(validation_accuracy_buffer)
                if index_of_max_val_acc==0:
                    break
                else:
                    del validation_accuracy_buffer[0]




