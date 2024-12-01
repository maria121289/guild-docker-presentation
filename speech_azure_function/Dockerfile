# To enable ssh & remote debugging on app service change the base image to the one below
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

ENV FUNCTIONS_WORKER_RUNTIME=python
ENV AzureWebJobsFeatureFlags=EnableWorkerIndexing

ENV AzureWebJobsStorage=
ENV BLOB_CONNECTION_STRING=
ENV AZURE_SPEECH_KEY=
ENV AZURE_SPEECH_REGION=

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y ffmpeg
# RUN apt-get install -y dnsutils

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot