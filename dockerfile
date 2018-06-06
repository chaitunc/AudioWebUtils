FROM python:2.7.13
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /AudioWebUtils
WORKDIR /AudioWebUtils
RUN pip install -r requirements.txt 
COPY ffmpeg /usr/local/bin
ENTRYPOINT ["python"]
CMD ["app.py"] 
