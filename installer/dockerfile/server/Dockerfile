
FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /app
#download scanflow

ENV SCANFLOW_PATH  /app/scanflow
ENV SERVER_HOME  ${SCANFLOW_PATH}/scanflow/server

RUN pip install mlflow==1.14.1
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns

WORKDIR $SERVER_HOME

CMD uvicorn server:app --reload --host 0.0.0.0 --port 8080