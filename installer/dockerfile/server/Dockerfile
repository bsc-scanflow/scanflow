FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /scanflow

#download scanflow
ENV SCANFLOW_PATH  /scanflow/scanflow
ENV SERVER_HOME  ${SCANFLOW_PATH}/scanflow/server

#scanflow
RUN pip install git+https://github.com/peiniliu/couler.git
RUN pip install kubernetes==12.0.1
#minio
RUN pip install boto3
RUN pip install mlflow==1.14.1

#server
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns

WORKDIR $SERVER_HOME

CMD uvicorn server:app --reload --host 0.0.0.0 --port 8080