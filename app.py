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


@app.route("/init")
def init():
    # Parse CLODUAMQP_URL (fallback to localhost)
    url = os.environ.get('RABBITMQ_BIGWIG_RX_URL')
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    connection = pika.SelectConnection(parameters=params,
                                   on_open_callback=on_open)
    try:
        # Step #2 - Block on the IOLoop
        connection.ioloop.start()
        # Catch a Keyboard Interrupt to make sure that the connection is closed cleanly
    except KeyboardInterrupt:
        # Gracefully close the connection
        connection.close()
        # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
        connection.ioloop.start()

# Step #3
def on_open(connection):
    connection.channel(on_channel_open)

# Step #4
def on_channel_open(channel):
    channel.queue_declare()
    channel.basic_consume(callback,
                      queue='findSegments',
                      no_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def callback(ch, method, properties, body):
    fileUrl = json.loads(body)
    print(" [x] Received %r" % fileUrl)
    fileId = fileUrl['id']
    print(fileId)
    accessToken = fileUrl['accessToken']
    print("submitting asyn task")
    credentials = AccessTokenCredentials(accessToken, 'my-user-agent/1.0')
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('drive', 'v2', http=http)
    url=service.files().get_media(fileId=fileId).execute()
    print(len(url))
    [Fs, x] = aIO.readAudioFileFromUrl(url)
    ShortTermFeatures = aS.silenceRemoval(x, Fs, 0.020, 0.020, smoothWindow = 1.0, Weight = 0.3, plot = False)
    [SVM, MEANSS, STDSS] = aS.step2(ShortTermFeatures)
    MaxIdx = aS.step3(ShortTermFeatures, MEANSS, STDSS, SVM, 0.020, smoothWindow = 1.0, Weight = 0.3)
    segments = aS.step4(MaxIdx,0.020)
    sendConnection = pika.BlockingConnection(pika.ConnectionParameters(
        host='127.0.0.1'))
    sendChannel = sendConnection.channel()
    returnData = {}
    returnData['segments'] = segments
    returnData['id'] = fileId
    message = json.dumps(returnData) 
    sendChannel.queue_declare(queue='getSegments')
    
    sendChannel.basic_publish(exchange='',
                          routing_key='getSegments',
                          body=message)
    print(" [x] Sent  %r" % message)
    sendConnection.close()
    print(" [x] Received %r")



@app.route("/")
def hello():
     return "Hello World!"

# endpoint to submitForSegments 
@app.route("/submitForSegments", methods=["POST"])
def submitForSegments():
    print("received request submitForSegments")
    fileUrl = request.get_json()
    fileId = fileUrl['id']
    print(fileId)
    accessToken = fileUrl['accessToken']
    print("submitting asyn task")
    credentials = AccessTokenCredentials(accessToken, 'my-user-agent/1.0')
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('drive', 'v2', http=http)
    url=service.files().get_media(fileId=fileId).execute()
    print(len(url))
    async_task = AsyncTask(fileId, url)
    async_task.start()
    return jsonify("Submitted")

@app.route("/getSegments", methods=["POST"])
def getSegments():
    print("received request getSegments")
    fileUrl = request.get_json()
    fileId = fileUrl['id']
    outputFile = open(fileId,"r")
    segments = outputFile.read()
    outputFile.close()
    print(segments)
    return jsonify(results = segments) 


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)
