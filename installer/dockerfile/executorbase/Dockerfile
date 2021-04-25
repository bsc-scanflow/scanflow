FROM continuumio/miniconda3
LABEL maintainer='scanflow'
    
RUN mkdir /app
WORKDIR /app

#RUN pip install scanflow

RUN pip install mlflow==1.14.1
#minio
RUN pip install boto3

CMD ["python", "/app/main.py"]