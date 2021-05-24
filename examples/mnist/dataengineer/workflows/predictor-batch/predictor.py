import mlflow
import click
import logging
import pandas as pd
import time
import numpy as np
import torch
import pytorch_lightning as pl
from pathlib import Path


import sys
sys.path.insert(0, '/scanflow/scanflow')

from scanflow.client import ScanflowTrackerClient

@click.command(help="batch predictions")
@click.option("--model_name", default='mnist_cnn', type=str)
@click.option("--model_version",  default=None, type=int)
@click.option("--model_stage",  default='Production', type=str)
@click.option("--input_data", help="New data",
              default='/workflow/load-data/mnist/data/mnist_c/brightness/test_images.npy', type=str)
def inference(model_name, model_version, model_stage, input_data):

    #data
    img_rows, img_cols = 28, 28
    x_test = np.load(input_data)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)


    #log
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))

    mlflow.set_experiment("predictor")
    with mlflow.start_run(run_name='predictor-batch'):

        #load model        
        if model_version is not None:
            model = mlflow.pytorch.load_model(
                model_uri=f"models:/{model_name}/{model_version}"
            )
            print(f"Loading model: {model_name}:{model_version}")
        else:
            model = mlflow.pytorch.load_model(
                model_uri=f"models:/{model_name}/{model_stage}"
            )
            print(f"Loading model: {model_name}:{model_stage}")
        
        predictions = predict(model, x_test)

            
        d_preds = {"predictions": predictions}
        df_preds = pd.DataFrame(d_preds)
        df_preds.to_csv("labels.csv", index=False)
        
        with open('images.npy', 'wb') as f:
            np.save(f, x_test)
        with open('labels.npy', 'wb') as f:
            np.save(f, predictions)

        mlflow.log_metric(key='n_predictions', value=len(df_preds))

        print(df_preds.head(10))

        mlflow.log_artifact('images.npy', artifact_path="data")
        mlflow.log_artifact('labels.npy', artifact_path="data")
        mlflow.log_artifact('labels.csv', artifact_path="data")

def predict(model, x_test):
    x_test_tensor = torch.Tensor(x_test)
    logits = model(x_test_tensor)
    preds = torch.argmax(logits, dim=1)
    
    return preds.cpu().detach().numpy()

if __name__ == '__main__':
    pl.seed_everything(42)
    inference()