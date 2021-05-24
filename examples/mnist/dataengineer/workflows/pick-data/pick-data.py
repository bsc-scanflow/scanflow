import mlflow
import click
import logging
import pandas as pd
import numpy as np
import time
import math
import os

from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, '/scanflow/scanflow')
from scanflow.client import ScanflowTrackerClient

import tensorflow as tf
from scipy.stats import gaussian_kde

RANDOM_STATE_SEED = 42


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

    x_grid = np.linspace(min(data), max(data), len(data))
    kdepdf = kde(data, x_grid, bandwidth=0.1, default=default)
    random_from_kde = generate_rand_from_pdf(kdepdf, x_grid)

    return random_from_kde

def picker(E_inference, x_inference, y_inference, n_critical_points=5):
    np.random.seed(RANDOM_STATE_SEED)
#     n_critical_points = 5
    request_list = list()

    for x_new, loss_mae, anomaly, preds in zip(x_inference,
                                    E_inference['Loss_mae'].values,
                                    E_inference['Anomaly'].values,
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
    n_critical_points

    return x_requests_critical, y_requests_critical


@click.command(help="Pick critical points")
@click.option("--E_inference", default='/workflow/detector-batch/E_inference.csv', type=str)
@click.option("--x_inference_artifact", default='/workflow/load-data/x_inference.npy', type=str)
@click.option("--y_inference_artifact", default='/workflow/load-data/y_inference.npy', type=str)
def pick(E_inference, x_inference_artifact, y_inference_artifact):
    
    #log
    mlflow.set_experiment("pick-data")
    with mlflow.start_run():
        
        img_rows, img_cols = 28, 28
        x_inference = np.load(x_inference_artifact)
        y_inference = np.load(y_inference_artifact)
        
        x_inference = x_inference.reshape(x_inference.shape[0], img_rows, img_cols)
        
        n_critical_points = int(x_inference.shape[0]*0.05)
        x_inference_chosen, y_inference_chosen = picker(E_inference, x_inference, y_inference, n_critical_points)

        with open('x_inference_chosen.npy', 'wb') as f:
            np.save(f, x_inference_chosen)
        with open('y_inference_chosen.npy', 'wb') as f:
            np.save(f, y_inference_chosen)
            
        mlflow.log_metric(key='n_critical_data', value=n_critical_points)
        mlflow.log_artifact('x_inference_chosen.npy',artifact_path="data")
        mlflow.log_artifact('y_inference_chosen.npy',artifact_path="data")          

if __name__ == '__main__':
    pick()