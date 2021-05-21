FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /scanflow

#download scanlfow
ENV SCANFLOW_PATH  /scanflow/scanflow
ENV AGENT_HOME  ${SCANFLOW_PATH}/scanflow/agent

RUN pip install git+https://github.com/peiniliu/couler.git
RUN pip install kubernetes==12.0.1
RUN pip install aiohttp

RUN pip install mlflow==1.14.1
#minio
RUN pip install boto3

# server
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns

WORKDIR $AGENT_HOME

ENTRYPOINT ["uvicorn main:agent --reload --host 0.0.0.0 --port 8080"]
