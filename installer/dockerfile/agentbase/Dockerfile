FROM continuumio/miniconda3
LABEL maintainer='scanflow'

RUN mkdir /scanflow

#download scanlfow
ENV SCANFLOW_PATH  /scanflow/scanflow
ENV AGENT_HOME  ${SCANFLOW_PATH}/scanflow/agent
RUN pip install APScheduler

RUN python3 -m pip install git+https://github.com/couler-proj/couler --ignore-installed
RUN pip install kubernetes==28.1.0
RUN pip install pyaml

RUN pip install mlflow==2.9.2
#minio
RUN pip install boto3

# server
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install aiohttp
RUN pip install aiodns
RUN pip install pydantic==1.10.14

WORKDIR $AGENT_HOME

ENTRYPOINT ["/bin/bash", "-c"]
