import os
import shutil
import zipfile
import mlflow
import click
import sklearn
import logging
import numpy as np
import pandas as pd

from mlflow.sklearn import log_model, save_model
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import ExtraTreesClassifier

random_state = 42
np.random.seed(random_state)

# exp_name = 'exp_workflow'
# artifact_location = os.path.join('hdfs:///tmp', exp_name)

@click.command(help="Create the model for the preprocessed data set")
@click.option("--preprocessed_data", help="Preprocessed data set path",
                default='./preprocessed_data.csv', type=str)
def modeling(preprocessed_data):

    with mlflow.start_run(run_name='modeling') as mlrun:
#         path = f'hdfs://{path}'



        df = pd.read_csv(preprocessed_data)
        logging.info(f'Dataset: {preprocessed_data} was read successfully ')

        class_name = 'species'
        X = df.loc[:, df.columns != class_name]
        y = df[class_name].copy()

        test_size = 0.2

#         X_train, X_test, y_train, y_test = train_test_split(
#                                 X, y, test_size=test_size, random_state=random_state)
        X_train, X_test, y_train, y_test = train_test_split(
                                X, y, test_size=test_size)

        # Later wrap the logs with scanflow log_metadata
        X_train.to_csv('X_train.csv', index=False)
        mlflow.log_artifact('X_train.csv')

        X_test.to_csv('X_test.csv', index=False)
        mlflow.log_artifact('X_test.csv')

        y_train.to_csv('y_train.csv', index=False)
        mlflow.log_artifact('y_train.csv')

        y_test.to_csv('y_test.csv', index=False)
        mlflow.log_artifact('y_test.csv')

        mlflow.log_param(key='x_train_len', value=len(X_train))
        mlflow.log_param(key='x_test_len', value=len(X_test))
        mlflow.log_param(key='test_percentage', value=test_size)
        mlflow.log_param(key='random_state_split', value=random_state)
#         dict_types = dict([(x,str(y)) for x,y in zip(X.columns, X.dtypes.values)])
#         mlflow.log_param(key='dtypes', value=dict_types)

        selectors = []
        # features.append(('transf_union', transf_union))
#         pca = PCA(n_components=9, random_state=random_state)
        pca = PCA(n_components=9)
        selectors.append(( 'pca', pca))
        # selectors.append(( 'select_best' , SelectKBest(k=3)))
        # features_union = FeatureUnion(feature_eng)

        # create pipeline
        estimators = []
        # estimators.append(( 'Features_union' , features_union))

#         et = ExtraTreesClassifier(n_estimators=20, random_state=random_state)
        et = ExtraTreesClassifier(n_estimators=20, n_jobs=1)

        mlflow.log_param(key='n_estimators_model', value=20)
        mlflow.log_param(key='random_state_model', value=random_state)

        estimators.append(( 'ET' , et))
        # estimators.append(('svm' , SVC(kernel="linear")))
        model = Pipeline([ ('selectors', FeatureUnion(selectors)),
                          ('estimators', et)])

        # evaluate pipeline on test dataset
        model.fit(X_train, y_train)
        test_acc = model.score(X_test, y_test)

        predictions = model.predict(X_test)
#         print(f'test: {y_test.values[-20:]}')
#         print(f'predictions: {predictions[-20:]}')

        mlflow.log_metric("test_acc", round(test_acc, 3))


        print(f'Accuracy: {round(test_acc, 3)}')

        # For production: Train the model with the whole dataset
        path_model = 'models'
        if os.path.isdir(path_model):
            shutil.rmtree(path_model, ignore_errors=True)
        else:
            save_model(model, path_model)

        log_model(model, path_model)

        # TODO: Check the right path of  the keras model (artifact)
#         mlflow.keras.log_model(model, "models")
        #     mlflow.keras.save_model(model, "keras-model")

#         mlflow.log_artifact(path, path_artifact)
#         mlflow.log_artifact('/root/project/ui_run', path_artifact)
#         return model, X_train, X_test, y_test


if __name__ == '__main__':
    modeling()

