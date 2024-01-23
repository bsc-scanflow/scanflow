import mlflow
import click
import logging
import pandas as pd
import time
import mlflow.pytorch
import shutil
import random
import numpy as np
import os
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, TensorSpec

import torchvision
import torch
import pytorch_lightning as pl
from torch import nn
from torch.nn import functional as F
from torchmetrics.functional import accuracy
from pl_bolts.datamodules import SklearnDataModule, SklearnDataset


import sys
sys.path.insert(0, '/scanflow/scanflow')

from scanflow.client import ScanflowTrackerClient

@click.command(help="Modeling")
@click.option("--model_name", default='mnist_cnn', type=str)
@click.option("--epochs", default='1', type=int)
@click.option("--x_train_path", default='/workflow/load-data/mnist/data/mnist/train_images.npy', type=str)
@click.option("--y_train_path", default='/workflow/load-data/mnist/data/mnist/train_labels.npy', type=str)
@click.option("--x_test_path", default='/workflow/load-data/mnist/data/mnist/test_images.npy', type=str)
@click.option("--y_test_path", default='/workflow/load-data/mnist/data/mnist/test_labels.npy', type=str)
@click.option("--x_newdata_path", default=None, type=str)
@click.option("--y_newdata_path", default=None, type=str)
@click.option("--retrain", default=False, type=bool)
@click.option("--model_version",  default=None, type=int)
@click.option("--model_stage",  default='Production', type=str)
def modeling(model_name, epochs, x_train_path, y_train_path, 
             x_test_path, y_test_path, x_newdata_path, y_newdata_path,
             retrain, model_version, model_stage):
    
    # data
    img_rows, img_cols = 28, 28
    if x_newdata_path is not None and y_newdata_path is not None:
        x_original_train = np.load(x_train_path)
        y_original_train = np.load(y_train_path)
        x_original_train = x_original_train.reshape(x_original_train.shape[0], img_rows, img_cols)

        x_new_train = np.load(x_newdata_path)
        y_new_train = np.load(y_newdata_path)

        x_train = np.concatenate((x_original_train, x_new_train), axis=0)
        y_train = np.concatenate((y_original_train, y_new_train), axis=0)
    else:
        x_train = np.load(x_train_path)
        y_train = np.load(y_train_path)
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols)

    x_test = np.load(x_test_path)
    y_test = np.load(y_test_path)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols)

    #log
    client = ScanflowTrackerClient(verbose=True)
    mlflow.set_tracking_uri(client.get_tracker_uri(True))
    logging.info("Connecting tracking server uri: {}".format(mlflow.get_tracking_uri()))
        
    mlflow.set_experiment("modeling_cnn1")
    with mlflow.start_run():
        #model    
        loaders_train = SklearnDataModule(X=x_train, 
                                    y=y_train, val_split=0.2, test_split=0,
                                         num_workers=4)

        if retrain:
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
        else:
            model = MNIST()
            
        trainer = pl.Trainer(max_epochs=epochs, 
                            #  progress_bar_refresh_rate=20,
                             deterministic=True,
                            #  checkpoint_callback=False, 
                             logger=False)
        trainer.fit(model, 
                    train_dataloaders=loaders_train.train_dataloader(), 
                    val_dataloaders=loaders_train.val_dataloader())


        score = evaluate(model, x_test, y_test)
        predictions = predict(model, x_test)
        
        input_schema = Schema([
          TensorSpec(np.dtype(np.float32), (-1, img_rows, img_cols)),
        ])
        output_schema = Schema([TensorSpec(np.dtype(np.float32), (-1, 10))])
        signature = ModelSignature(inputs=input_schema, outputs=output_schema)
        
#         signature = infer_signature(x_test, predictions)
        mlflow.pytorch.log_model(model, artifact_path=model_name, 
                                 signature=signature, 
                                 registered_model_name=model_name)
#                                  input_example=x_test[:2])
        
        mlflow.log_metric(key='accuracy', value=round(score, 2))
        mlflow.log_metric(key='training_dataset_len', value=x_train.shape[0])


class MNIST(pl.LightningModule):
    
    def __init__(self, hidden_size=64, 
                 learning_rate=2e-4):

        super().__init__()
        
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate

        self.num_classes = 10
        self.dims = (1, 28, 28)
        channels, width, height = self.dims

        # Define PyTorch model
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(channels * width * height, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, self.num_classes)
        )

    def forward(self, x):
#         x = x.type(torch.FloatTensor)
        x = torch.Tensor(x)
        x = x.type(torch.FloatTensor)
#         x = x.reshape(-1, 28, 28)
        x = self.model(x)
        return F.log_softmax(x, dim=1)

    def training_step(self, batch, batch_idx: int):
        x, y = batch
        y = y.type(torch.LongTensor)
        logits = self(x)
        loss = F.nll_loss(logits, y)
        return loss

    def validation_step(self, batch, batch_idx: int):
        x, y = batch
        y = y.type(torch.LongTensor)
        logits = self(x)
        loss = F.nll_loss(logits, y)
        preds = torch.argmax(logits, dim=1)
        acc = self.accuracy(preds, y, task="multiclass", num_classes=self.num_classes)

        print(f"val_acc={acc}")
        return loss

    def test_step(self, batch, batch_idx: int):
        
        return self.validation_step(batch, batch_idx)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        return optimizer
    
def evaluate(model, x_test, y_test):
    x_test_tensor = torch.Tensor(x_test)
    y_test_tensor = torch.Tensor(y_test)
    y_test_tensor = y_test_tensor.type(torch.LongTensor)
    
    logits = model(x_test_tensor)
    preds = torch.argmax(logits, dim=1)
    score = accuracy(preds, y_test_tensor,task="multiclass", num_classes=10)
    
    return score.cpu().detach().tolist()
    
def predict(model, x_test):
    x_test_tensor = torch.Tensor(x_test)
    logits = model(x_test_tensor)
    preds = torch.argmax(logits, dim=1)
    
    return preds.cpu().detach().numpy()

if __name__ == '__main__':
    pl.seed_everything(42)
    modeling()
