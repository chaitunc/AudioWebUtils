from __future__ import print_function
from tempfile import TemporaryFile, NamedTemporaryFile
from flask import Flask, request, jsonify
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from io import BytesIO
from oauth2client.client import AccessTokenCredentials
from flask import stream_with_context, request, Response, json
from asyncTask import AsyncTask
import audioBasicIO as aIO
import audioSegmentation as aS 
import httplib2
import os
import os.path
import logging
import pika
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)


@app.route("/boot")
def boot():
     async_task = AsyncTask()
     async_task.start()
     return "Starting Queues!"

@app.route("/")
def hello():
     return "Hello World!"
 
if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
