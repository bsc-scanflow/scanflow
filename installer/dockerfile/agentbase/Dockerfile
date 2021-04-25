FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /agent
WORKDIR /agent

#RUN pip install scanflow

RUN pip install mlflow==1.14.1
#minio
RUN pip install boto3

# server
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns

CMD uvicorn main:agent --reload --host 0.0.0.0 --port 8080
