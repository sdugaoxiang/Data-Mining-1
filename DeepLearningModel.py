from __future__ import print_function
import tensorflow as tf
import numpy as np
import os
import pandas as pd
from sklearn.metrics import matthews_corrcoef
import matplotlib.pyplot as plt
import csv
from sklearn.cross_validation import train_test_split

model_name = 'model'
model_path = '/home/sandareka/Tensorflow/Data_Mining_Project' #'F:/Data Mining Project/Models' #path to save the model

is_GPU = True

if is_GPU == True:
    device_name = "/gpu:0"
else:
    device_name = "/cpu:0"


def csv_to_numpy_array(filePath, delimiter):
    return np.genfromtxt(filePath, delimiter=delimiter, dtype=None)

def import_data():
    print("loading training and validation data")
    dataX =  np.delete(np.genfromtxt("data_nn/pre_processed_training_data_11_10_3.csv", delimiter=","), 0, axis=0)
    dataY = np.delete(np.genfromtxt("data_nn/training_labels_11_10_3.csv", delimiter=","), 0, axis=0)
    trainX, validationX, trainY, validationY = train_test_split(dataX, dataY, test_size=0.1, random_state=100)

    print("loading testing data")
    testX = np.delete(np.genfromtxt("data_nn/pre_processed_testing_data_11_10_3.csv", delimiter=","), 0, axis=0)
    return trainX,trainY,validationX,validationY,testX

#Given the label returns one hot representation of that lable
def convert_to_one_hot_representation(data_set):
    new_data_set = np.zeros(shape=(len(data_set), 2))
    for i in range(len(data_set)):
        new_data_set[i, int(data_set[i])] = 1

    return new_data_set

def write_output_file(output_file, output):
    with open(output_file, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for r in range(len(output)):
            output_Text = [r,output[r]]
            writer.writerow(output_Text)

trainX,train_label,validationX,validation_label,testX = import_data()

trainY = convert_to_one_hot_representation(train_label)
validationY = convert_to_one_hot_representation(validation_label)

# Parameters
learning_rate = 0.0001
training_epochs = 1000
batch_size = 50
display_step = 1
positive_class_frequency = 0.12
negative_class_frequency = 0.88

#200 x 4, 0.0001, 1000, 57.49

# Network Parameters
n_hidden_1 = 64#2048#512#128#2500#256 # 1st layer number of neurons
n_hidden_2 = 64#1024#256#64#2000#256 # 2nd layer number of neurons
n_hidden_3 = 64#512#1500#256 # 3rd layer number of neurons
n_hidden_4 = 64#512#200 # 4th layer number of neurons
n_hidden_5 = 64
n_hidden_6 = 64
n_hidden_7 = 64
n_input = trainX.shape[1] # Number of features
n_classes = 2 #Binary classification

with tf.device(device_name):
    # tf Graph input
    X = tf.placeholder("float", [None, n_input])
    Y = tf.placeholder("float", [None, n_classes])
    dropout_keep_prob = tf.placeholder(tf.float32)

    initializer = tf.contrib.layers.xavier_initializer()

    # Store layers weight & bias
    weights = {
        'h1': tf.Variable(initializer([n_input, n_hidden_1])),
        'h2': tf.Variable(initializer([n_hidden_1, n_hidden_2])),
        'h3': tf.Variable(initializer([n_hidden_2, n_hidden_3])),
        'h4': tf.Variable(initializer([n_hidden_3, n_hidden_4])),
        'h5': tf.Variable(initializer([n_hidden_4, n_hidden_5])),
        'h6': tf.Variable(initializer([n_hidden_5, n_hidden_6])),
        'h7': tf.Variable(initializer([n_hidden_6, n_hidden_7])),
        'out': tf.Variable(initializer([n_hidden_7, n_classes]))
    }
    biases = {
        'b1': tf.Variable(tf.zeros([n_hidden_1])),
        'b2': tf.Variable(tf.zeros([n_hidden_2])),
        'b3': tf.Variable(tf.zeros([n_hidden_3])),
        'b4': tf.Variable(tf.zeros([n_hidden_4])),
        'b5': tf.Variable(tf.zeros([n_hidden_5])),
        'b6': tf.Variable(tf.zeros([n_hidden_6])),
        'b7': tf.Variable(tf.zeros([n_hidden_7])),
        'out': tf.Variable(tf.zeros([n_classes]))
    }


    # Create model
    def multilayer_perceptron(x):
        # Hidden fully connected layer with 256 neurons
        layer_1 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(x, weights['h1']), biases['b1'])), dropout_keep_prob)
        # Hidden fully connected layer with 256 neurons
        layer_2 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])), dropout_keep_prob)
        # Hidden fully connected layer with 256 neurons
        layer_3 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_2, weights['h3']), biases['b3'])), dropout_keep_prob)

        layer_4 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_3, weights['h4']), biases['b4'])), dropout_keep_prob)

        layer_5 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_4, weights['h5']), biases['b5'])), dropout_keep_prob)

        layer_6 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_5, weights['h6']), biases['b6'])), dropout_keep_prob)

        layer_7 = tf.nn.dropout(tf.nn.tanh(tf.add(tf.matmul(layer_6, weights['h7']), biases['b7'])), dropout_keep_prob)
        # Output fully connected layer with a neuron for each class
        out_layer = tf.nn.tanh(tf.add(tf.matmul(layer_7, weights['out']),biases['out']))
        return out_layer


    # Construct model
    logits = multilayer_perceptron(X)

    softmaxed_logits = tf.nn.softmax(logits=logits,dim=1)
    predicted_results = tf.argmax(softmaxed_logits, 1)

    #predicted_results = tf.greater(softmaxed_logits, 1)

    # Define loss and optimizer

    loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
        logits=logits, labels=Y))
    global_step = tf.Variable(0, trainable=False)
    learning_rate = tf.train.exponential_decay(learning_rate, global_step, int(trainX.shape[0] / batch_size),0.95)
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)
    # Initializing the variables
    init = tf.global_variables_initializer()

with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:

    saver = tf.train.Saver(max_to_keep=100)
    global_step = tf.Variable(0, trainable=False)
    sess.run(init)
    losses = []
    mean_loss_for_epoch = []
    mcc_scores = []
    best_mcc = 0


    # Training cycle
    for epoch in range(training_epochs):
        index = (np.arange(len(trainX)).astype(int))
        np.random.shuffle(index)
        for start, end in zip(range(0, len(index), batch_size), range(batch_size, len(index), batch_size)):
            batch_x = trainX[index[start:end]]
            batch_y = trainY[index[start:end]]
            dropout_keep_prob_input = 0.5#0.5
            # Run optimization op (backprop) and cost op (to get loss value)
            _, loss_value = sess.run([train_op, loss_op], feed_dict={X: batch_x,
                                                            Y: batch_y, dropout_keep_prob:dropout_keep_prob_input})
            # Print average loss for the batch
            print("Current Cost: ", loss_value, "\t Epoch {}/{}".format(epoch, training_epochs),
                  "\t Iter {}/{}".format(start, len(trainX)))
            losses.append(loss_value)
        #Average loss for the epoch
        mean_loss_for_epoch.append(np.mean(losses))
        print("Mean loss for the epoch", mean_loss_for_epoch[epoch])

        #Validation-------------------------------------
        #Predict class for the validation set and calculate MCC score
        dropout_keep_prob_input = 1.0
        returned_predicted_results = sess.run(predicted_results, feed_dict={X: validationX, Y: validationY, dropout_keep_prob:dropout_keep_prob_input})
        mcc_score = matthews_corrcoef(validation_label, returned_predicted_results)
        print("MCC Score: ", mcc_score)
        mcc_scores.append(mcc_score)

        #Save model with the best validation results
        if best_mcc< mcc_score:
            best_mcc = mcc_score
            print("Saving the model from epoch: ", epoch)
            saver.save(sess, os.path.join(model_path, model_name), global_step=epoch)

    plt.rcParams['figure.figsize'] = (10.0, 8.0)  # set default size of plots
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    plt.plot(mean_loss_for_epoch, '-o')
    plt.xlabel('epoch')
    plt.ylabel('training loss')
    plt.savefig('training_loss.png')
    plt.clf()

    plt.rcParams['figure.figsize'] = (10.0, 8.0)  # set default size of plots
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    plt.plot(mcc_scores, '-o')
    plt.xlabel('epoch')
    plt.ylabel('validation mcc score')
    plt.savefig('validation_mcc.png')

    print("Optimization Finished!")
    print("Best MCC Score Achieved",best_mcc)

"""
with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
    # Test model
    saver = tf.train.Saver()
    saved_path = tf.train.latest_checkpoint(model_path)
    saver.restore(sess, saved_path)
    dropout_keep_prob_input = 1.0
    logits = multilayer_perceptron(X)
    softmaxed_logits = tf.nn.softmax(logits=logits, dim=1)
    weighted_results = softmaxed_logits
    predicted_results = tf.argmax(softmaxed_logits, 1)
    returned_predicted_results = sess.run(predicted_results, feed_dict={X: testX,dropout_keep_prob: dropout_keep_prob_input})
    write_output_file("results_11_10_4.csv",returned_predicted_results)
"""

