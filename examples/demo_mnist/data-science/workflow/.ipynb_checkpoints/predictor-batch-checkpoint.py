import mlflow
import click
import logging
import pandas as pd
import time
import predictor_utils
import numpy as np
import torch

from pathlib import Path

@click.command(help="Gather an input data set")
@click.option("--input_path", help="Input raw data set",
              default='./mnist_sample/test_images.npy', type=str)
@click.option("--model_name", default='mnist_cnn', type=str)
@click.option("--model_version",  default=16, type=int)
def predictor(input_path, model_name, model_version):
    with mlflow.start_run(run_name='predictor') as mlrun:

        img_rows, img_cols = 28, 28
        x_test = np.load(input_path)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)
        
        model = mlflow.pytorch.load_model(
            model_uri=f"models:/{model_name}/{model_version}"
        )
        predictions = predictor_utils.predict_model(model, x_test)

        d_preds = {"predictions": predictions}
        df_preds = pd.DataFrame(d_preds)
        df_preds.to_csv("preds.csv", index=False)
        
        with open('input.npy', 'wb') as f:
            np.save(f, x_test)

        mlflow.log_param(key='n_predictions', value=len(df_preds))
        input_size = round(Path('input.npy').stat().st_size / (1024), 2)
        mlflow.log_param(key='input_size', value=f"{input_size} KB")
        print(df_preds.head(10))

        mlflow.log_artifact('preds.csv')
        mlflow.log_artifact('input.npy')


if __name__ == '__main__':
    predictor()
