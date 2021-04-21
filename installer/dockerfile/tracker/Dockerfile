FROM continuumio/miniconda3
LABEL maintainer='scanflow'

ENV MLFLOW_HOST  0.0.0.0
ENV MLFLOW_PORT  5000

RUN pip install mlflow==1.14.1
RUN pip install psycopg2-binary
RUN pip install boto3

CMD mlflow server                  --backend-store-uri $MLFLOW_STORAGE                 --default-artifact-root $MLFLOW_ARTIFACT                 --host $MLFLOW_HOST -p $MLFLOW_PORT