FROM continuumio/miniconda3
LABEL maintainer='scanflow'

ENV MLFLOW_HOST  0.0.0.0
ENV MLFLOW_PORT  5000

#2.9.2
RUN pip install mlflow
#postgre
RUN pip install psycopg2-binary 
#minio
RUN pip install boto3

CMD mlflow server                  --backend-store-uri $TRACKER_STORAGE                 --default-artifact-root $TRACKER_ARTIFACT                 --host $MLFLOW_HOST -p $MLFLOW_PORT
