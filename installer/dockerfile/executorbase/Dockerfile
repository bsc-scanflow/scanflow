FROM continuumio/miniconda3
LABEL maintainer='scanflow'
    
RUN mkdir /app
WORKDIR /app

RUN mkdir /workflow
ENV SCANFLOW_WORKFLOW_OUTPUT_DIR /workflow

#RUN pip install scanflow
RUN pip install git+https://github.com/peiniliu/couler.git
RUN pip install kubernetes==12.0.1
RUN pip install aiohttp

RUN pip install mlflow==1.14.1
#minio
RUN pip install boto3

ENTRYPOINT ["python", "/app/main.py"]