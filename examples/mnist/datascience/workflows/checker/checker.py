import mlflow
from mlflow.tracking import MlflowClient
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

def get_loss(model, x, change_score=False):

    x_pred = model.predict(x)
    x = x.reshape(x.shape[0], 28, 28)
    x_pred = x_pred.reshape(x_pred.shape[0], 28, 28)
    E = pd.DataFrame()

    sz = len(x)
    reconstruction_cost = np.array([np.linalg.norm(np.subtract(x[i],x_pred[i])) for i in range(0,sz)])
    score_anomaly = (reconstruction_cost - np.min(reconstruction_cost)) / np.max(reconstruction_cost)

    if change_score:
        E['Loss_mae'] = 1 - score_anomaly
    else:
        E['Loss_mae'] = score_anomaly

    return E

def decide_threshold(ddae_model, x_train):

    width = 0.1
    quantile_high = 0.95
    quantile_low = 1.0 - quantile_high

    # Use default score_anomaly
    E_train = get_loss(ddae_model, x_train, change_score=False)
    # Define threshold
    THRESHOLD_HIGH = E_train['Loss_mae'].quantile(q=quantile_high)
    THRESHOLD_LOW = E_train['Loss_mae'].quantile(q=quantile_low)

    return THRESHOLD_HIGH, THRESHOLD_LOW


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
    with mlflow.start_run() as run:
        #modeling
        detector, ddae_history = train(x_train, 
                                        epochs=epochs, 
                                        batch_size=128,
                                        model_path='detector.hdf5')

        #decide threshold
        THRESHOLD_HIGH, THRESHOLD_LOW  = decide_threshold(detector,
                                                    x_train)

        #log run
        mlflow.keras.log_model(detector, artifact_path=model_name, 
                                   registered_model_name=model_name)
        mlflow.log_param(key='THRESHOLD_HIGH', value=THRESHOLD_HIGH)
        mlflow.log_param(key='THRESHOLD_LOW', value=THRESHOLD_LOW)

        epoch = 1
        for val in ddae_history.history['val_loss']:
            mlflow.log_metric(key='history_val_loss', value=val, step=epoch)
            epoch = epoch + 1
        
        mlflow.log_metric(key='val_loss', value=ddae_history.history['val_loss'][-1])

        #log model
        mlflowClient = MlflowClient(client.get_tracker_uri(True))
        mv = mlflowClient.search_model_versions("run_id='{}'".format(run.info.run_id))
        mlflowClient.set_model_version_tag(model_name, mv[0].version, "THRESHOLD_HIGH", THRESHOLD_HIGH)
        mlflowClient.set_model_version_tag(model_name, mv[0].version, "THRESHOLD_LOW", THRESHOLD_LOW)
        
        
if __name__ == '__main__':
    checker()
