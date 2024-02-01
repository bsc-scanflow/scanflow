FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /scanflow

#download scanflow
ENV SCANFLOW_PATH  /scanflow/scanflow
ENV SERVER_HOME  ${SCANFLOW_PATH}/scanflow/server

#scanflow
RUN python3 -m pip install git+https://github.com/couler-proj/couler --ignore-installed
RUN pip install kubernetes==28.1.0
RUN pip install pyaml
#minio
RUN pip install boto3
RUN pip install mlflow==2.9.2

#server
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns
RUN pip install pydantic==1.10.14

WORKDIR $SERVER_HOME

CMD uvicorn server:app --reload --host 0.0.0.0 --port 8080
