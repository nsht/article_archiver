FROM python:3.6

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

RUN mkdir /article_archiver_api

WORKDIR /article_archiver_api

ADD . /article_archiver_api/

RUN pip install -r requirements.txt

