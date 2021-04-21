import os
import mlflow
import click
import logging
import pandas as pd

from datetime import datetime

#print(mlflow.__version__) # it must be at least 1.0

# uri = '/root/project/mlruns'
exp_name = f'single_{datetime.now().strftime("%Y%m%d-%H%M%S")}'
# mlflow.set_tracking_uri('http://tracker_workflow1:8001')


@click.command(help="New raw data for predicting")
@click.option("--new_data_path", help="Input new raw data set",
              default='new_data.csv', type=str)
def get_new_data(new_data_path):
    with mlflow.start_run(run_name='get_new_data') as mlrun:

        # names = ['species', 'specimen_number', 'eccentricity', 'aspect_ratio',
        #         'elongation', 'solidity', 'stochastic_convexity', 'isoperimetric_factor',
        #         'maximal_indentation_depth', 'lobedness', 'average_intensity',
        #         'average_contrast', 'smoothness', 'third_moment', 'uniformity', 'entropy']

        df = pd.read_csv(new_data_path)
        # df = pd.read_csv(new_data_path, names=names)
        # logging.info(f'Dataset: {new_data_path} was read successfully ')

        print(df.head())

        df.to_csv('gathered.csv', index=False)
        mlflow.log_artifact('gathered.csv')


if __name__ == '__main__':
    get_new_data()
