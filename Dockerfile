FROM python:3.7

# Working directory for the application
ENV APPLICATION_ROOT /src/
RUN mkdir -p $APPLICATION_ROOT
WORKDIR $APPLICATION_ROOT

# Install required modules
ADD requirements.txt $APPLICATION_ROOT
RUN pip install -r requirements.txt

ADD . $APPLICATION_ROOT
