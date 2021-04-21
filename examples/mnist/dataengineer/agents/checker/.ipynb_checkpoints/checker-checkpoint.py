import mlflow
import click
import logging
import pandas as pd
import numpy as np
import time
import checker_utils
import numpy as np
import tensorflow as tf
import math
import os

from datetime import datetime
from pathlib import Path

@click.command(help="Check anomalies")
@click.option("--input_path", help="Input raw data set",
              default='./images', type=str)
@click.option("--checker_path", help="Input raw data set",
              default='./checker.hdf5', type=str)
def checker(input_path, checker_path):
    with mlflow.start_run(run_name='checker') as mlrun:

        img_rows, img_cols = 28, 28
        x_test = np.load(input_path)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)
        
        date = datetime.today()

        checker, E_full, E_test, test = checker_utils.get_checker(x_test, x_test, 
                                                    epochs=50, 
                                                    model_path=checker_path,
                                                    date=date, 
                                                    wanted_anomalies=50)



        E_full.to_csv("E_full.csv", index=True)
        E_test.to_csv("E_test.csv", index=True)
        

        mlflow.log_param(key='n_anomalies', value=sum(E_test['Anomaly']))
 
        print(E_test.head())

        mlflow.log_artifact('E_full.csv')
        mlflow.log_artifact('E_test.csv')


if __name__ == '__main__':
    checker()
