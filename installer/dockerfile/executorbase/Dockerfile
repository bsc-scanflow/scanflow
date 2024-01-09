FROM continuumio/miniconda3
LABEL maintainer='scanflow'
    
RUN mkdir /app
WORKDIR /app

RUN mkdir /workflow
ENV SCANFLOW_WORKFLOW_OUTPUT_DIR /workflow

#RUN pip install scanflow
RUN python3 -m pip install git+https://github.com/couler-proj/couler --ignore-installed
RUN pip install kubernetes==28.1.0
RUN pip install aiohttp
RUN pip install pyaml

RUN pip install mlflow==2.9.2
#minio
RUN pip install boto3

ENTRYPOINT ["python", "/app/main.py"]