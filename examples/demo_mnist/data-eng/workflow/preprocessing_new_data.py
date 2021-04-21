import os
import mlflow
import click
import sklearn
import logging
import pandas as pd


@click.command(help="Preprocess the gathered data set")
@click.option("--gathered_data", help="Input gathered data set",
              default='./gathered.csv', type=str)
@click.option("--output_data", help="Preprocessed data",
              default='preprocessed_data.csv', type=str)
def preprocessing(gathered_data, output_data):
    with mlflow.start_run(run_name='preprocessing') as mlrun:

        # logging.info(f'Dataset: {gathered_data} was read successfully ')

        # Some preprocessing steps here
        df = pd.read_csv(gathered_data)
        df_cleaned = df.loc[:, df.columns != 'specimen_number'].copy()
        df_cleaned[df_cleaned.columns] = df_cleaned[df_cleaned.columns].astype(float)
        # df_cleaned['species'] = df_cleaned['species'].astype(int)

        # logs some metadata
        mlflow.log_param(key='n_samples', value=len(df_cleaned))
        mlflow.log_param(key='n_features', value=len(df_cleaned.columns))
        dict_types = dict([(x,str(y)) for x,y in zip(df_cleaned.columns, df_cleaned.dtypes.values)])
        mlflow.log_param(key='dtypes', value=dict_types)
        # mlflow.log_param(key='n_classes', value=len(df_cleaned['species'].unique()))
        mlflow.log_param(key='problem_type', value='classification')

        df_cleaned.to_csv(output_data, index=False)
        mlflow.log_artifact(output_data)
        # logging.info(f'Preprocessed dataset was saved successfully')


if __name__ == '__main__':
    preprocessing()
