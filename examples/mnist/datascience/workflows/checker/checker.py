import mlflow
import click
import logging
import pandas as pd
import numpy as np
import tensorflow as tf
import math
import os

from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/scanflow/scanflow')

from scanflow.client import ScanflowTrackerClient


import tensorflow as tf
from scipy.stats import gaussian_kde

from tensorflow.keras.layers import Input, Dropout, Dense, Activation, Flatten, BatchNormalization
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, LeakyReLU
from tensorflow.keras.models import Model, Sequential

RANDOM_STATE_SEED = 42

def deep_denoise_ae():
    input_img = Input(shape=(28, 28, 1))

    x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    encoded = MaxPooling2D((2, 2), padding='same')(x)

    # at this point the representation is (4, 4, 8) i.e. 128-dimensional

    x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(16, (3, 3), activation='relu')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = Model(input_img, decoded)

    return autoencoder


def scale(x):
    img_rows, img_cols = 28, 28
    # x = df.values
    x = x.reshape(x.shape[0], img_rows, img_cols, 1)
    x = x.astype('float32')
    x /= 255

    return x

def get_loss(model, x, x_index, change_score=False):

    x_pred = model.predict(x)
    x = x.reshape(x.shape[0], 28, 28)
    x_pred = x_pred.reshape(x_pred.shape[0], 28, 28)
    E = pd.DataFrame(index=x_index)

    sz = len(x)
    reconstruction_cost = np.array([np.linalg.norm(np.subtract(x[i],x_pred[i])) for i in range(0,sz)])
    score_anomaly = (reconstruction_cost - np.min(reconstruction_cost)) / np.max(reconstruction_cost)

    if change_score:
        E['Loss_mae'] = 1 - score_anomaly
    else:
        E['Loss_mae'] = score_anomaly

    return E

def decide_threshold(ddae_model, x_train, x_train_index,
                      x_test, x_test_index, wanted_anomalies=10):

    width = 0.1
    quantile_high = 0.95
    quantile_low = 1.0 - quantile_high
    # if n_anomalies:
    for trials in range(1, 3): # Iterate until 0.6, 0.4

      # Use default score_anomaly
        E_train = get_loss(ddae_model, x_train, x_train_index, change_score=False)
        # Define threshold
        THRESHOLD_HIGH = E_train['Loss_mae'].quantile(q=quantile_high)
        THRESHOLD_LOW = E_train['Loss_mae'].quantile(q=quantile_low)
        # Get AE loss on test
        E_test = get_loss(ddae_model, x_test, x_test_index, change_score=False)


        high =  E_test['Loss_mae'] > THRESHOLD_HIGH
        low =  E_test['Loss_mae'] < THRESHOLD_LOW

        # print(high | low)
        E_test['Anomaly'] = high | low

        E_full = pd.concat([E_train, E_test], sort=False)
        # E_full['Threshold2'] = NAIVE_THRESHOLD
        E_full['Threshold_high'] = THRESHOLD_HIGH
        E_full['Threshold_low'] = THRESHOLD_LOW

        n_anomalies = sum(E_test['Anomaly'])
        print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
        if sum(E_test['Anomaly']) >= wanted_anomalies:
        # print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
            break
        quantile_high = quantile_high - width
        quantile_low = 1.0 - quantile_high

          # print(quantile_high)


    return E_train, E_test, E_full

def get_detector(x_train_, x_test, date=None,
                epochs=25, model_path='checker.hdf5', wanted_anomalies=10):
    #np.random.seed(RANDOM_STATE_SEED)
    #tf.random.set_seed(RANDOM_STATE_SEED)

    # pdb.set_trace()
    x_train_index = None
    x_test_index = None

    if date is not None:
        range_periods = x_train_.shape[0] + x_test.shape[0]
        concat_indexes = pd.date_range(date, freq="0.1ms",
                                       periods=range_periods)
        x_train_index = concat_indexes[:x_train_.shape[0]]
        x_test_index = concat_indexes[x_train_.shape[0]:]

    x_train_ = scale(np.copy(x_train_))
    x_test = scale(np.copy(x_test))

    # x_train_noisy = add_noise(x_train_)

    if os.path.isfile(model_path):
        print("[+] Loading Checker")
        ddae_model = tf.keras.models.load_model(model_path)
    else:
        print("[+] Training Checker")
        NUM_EPOCHS=epochs

        BATCH_SIZE=128
        # BATCH_SIZE = 32

        ddae_model = deep_denoise_ae()
        ddae_model.compile(optimizer='adadelta',
                           loss='mse')
        ddae_history = ddae_model.fit(x_train_, x_train_ , # x_train_noisy x_train_
                                      batch_size=BATCH_SIZE,
                                      epochs=NUM_EPOCHS,
                                      validation_split=0.1,
                                      #                   validation_data=(X_test_noisy, X_test),
                                      verbose=1)
        ddae_model.save(model_path)

    E_train, E_test, E_full  = decide_threshold(ddae_model,
                                                        x_train_, x_train_index,
                                                        x_test, x_test_index,
                                                        wanted_anomalies)


    x_test_df = pd.DataFrame(x_test_index)

    return ddae_model, E_full, E_test, x_test_df

def train(x_train, epochs=25, batch_size=128, model_path='checker.hdf5'):

    x_train = scale(np.copy(x_train))

    print("[+] Training Checker")
    NUM_EPOCHS=epochs

    BATCH_SIZE=batch_size
    # BATCH_SIZE = 32

    ddae_model = deep_denoise_ae()
    ddae_model.compile(optimizer='adadelta',
                       loss='mse')
    ddae_history = ddae_model.fit(x_train, x_train , # x_train_noisy x_train_
                                  batch_size=BATCH_SIZE,
                                  epochs=NUM_EPOCHS,
                                  validation_split=0.1,
                                  verbose=1)
    ddae_model.save(model_path)

    return ddae_model, ddae_history

def kde(x, x_grid, bandwidth=0.2, default=False):

    kde = gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1))
    if default:
        kde = gaussian_kde(x)

    return kde.evaluate(x_grid)

def generate_rand_from_pdf(pdf, x_grid):
    np.random.seed(RANDOM_STATE_SEED)
    cdf = np.cumsum(pdf)
    cdf = cdf / cdf[-1]
    values = np.random.rand(len(pdf))
    value_bins = np.searchsorted(cdf, values)
    random_from_cdf = x_grid[value_bins]

    return random_from_cdf

def choice_from_anomalous(anomalous_loss, default=True):
    data = anomalous_loss
    # hist, bins = np.histogram(data, bins=50)

    x_grid = np.linspace(min(data), max(data), len(data))
    kdepdf = kde(data, x_grid, bandwidth=0.1, default=default)
    random_from_kde = generate_rand_from_pdf(kdepdf, x_grid)

    # bin_midpoints = bins[:-1] + np.diff(bins) / 2
    # random_from_cdf = generate_rand_from_pdf(hist, bin_midpoints)

    # plt.subplot(121)
    # plt.hist(data, 50)
    # plt.subplot(122)
    # plt.hist(random_from_kde, 50)
    # plt.show();

    return random_from_kde

def picker(E_test, x_inference, y_inference, n_critical_points=5):
    np.random.seed(RANDOM_STATE_SEED)
#     n_critical_points = 5
    request_list = list()
#     checker, E_full, E_test, test = get_checker(x_train, x_new_c_, 
#                                               epochs=epochs_anomaly, 
#                                               date=date, 
#                                               wanted_anomalies=n_critical_points)

#     predictions = predict_model(model_mnist, x_new_c_)

    for x_new, loss_mae, anomaly, preds in zip(x_inference,
                                    E_test['Loss_mae'].values,
                                    E_test['Anomaly'].values,
#                                     y_new_c_,
                                    y_inference):

        data = dict()
        data['x_new'] = x_new
        data['loss_mae'] = loss_mae
        data['anomaly'] = anomaly
    #     data['y_new'] = y_new
        data['preds'] = preds

        request_list.append(data)

    n_anomalies = sum([d['anomaly'] for d in request_list])
    anomalous_loss = np.array([d['loss_mae'] for d in request_list if d['anomaly']])
    print(len(anomalous_loss))
    chosen_distribution = choice_from_anomalous(anomalous_loss, default=True)

    chosen_loss = np.random.choice(anomalous_loss,
                              p=chosen_distribution/sum(chosen_distribution),
                              size=n_critical_points, replace=False)
    # plt.hist(chosen_loss);
    print(set(chosen_loss).issubset(anomalous_loss))
    print(f"Mean real {np.mean(anomalous_loss)} | Mean sampled: {np.mean(chosen_loss)}")
    print(f"Chosen: {len(chosen_loss)}")

#     print(f"critical_points: {n_critical_points}")

    x_requests_critical = np.array([d['x_new'] for d in request_list if d['loss_mae'] in chosen_loss])
    y_requests_critical = np.array([d['preds'] for d in request_list if d['loss_mae'] in chosen_loss])

    return x_requests_critical, y_requests_critical




@click.command(help="Train a detector")
@click.option("--model_name", default='mnist_detector', type=str)
@click.option("--epochs", default=1, type=int)
@click.option("--x_train_path", default='/workflow/load-data/mnist/data/mnist/train_images.npy', type=str)
def checker(model_name, epochs, x_train_path):

    #data
    img_rows, img_cols = 28, 28
    x_train = np.load(x_train_path)
    
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)
    

    #log
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True)) 
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

    mlflow.set_experiment("checker")
    with mlflow.start_run():
        #modeling
        detector, ddae_history = train(x_train, 
                                        epochs=epochs, 
                                        batch_size=128,
                                        model_path='detector.hdf5')
        mlflow.keras.log_model(detector, artifact_path=model_name, 
                                   registered_model_name=model_name)
        
        mlflow.log_param(key='val_loss', value=ddae_history.history['val_loss'])


if __name__ == '__main__':
    checker()
