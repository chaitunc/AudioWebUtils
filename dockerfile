FROM python:2.7.13
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /AudioWebUtils
WORKDIR /AudioWebUtils
RUN pip install -r requirements.txt 
COPY ffmpeg /usr/local/bin
COPY ffprobe /usr/local/bin
RUN chmod +x /usr/local/bin/ffmpeg
RUN chmod +x /usr/local/bin/ffprobe
ENV PATH="/usr/local/bin:${PATH}"
CMD gunicorn --bind 0.0.0.0:$PORT app:app
