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
import audioBasicIO as aIO
import audioSegmentation as aS 
import httplib2
import os
import os.path
import logging
import pika
from oauth2client.service_account import ServiceAccountCredentials

import threading  
class AsyncTask(threading.Thread):
    def __init__(self):
        super(AsyncTask,self).__init__()
    # Step #3
    def on_open(self,connection):
        connection.channel(self.on_channel_open)
    
    # Step #4
    def on_channel_open(self,channel):
        channel.queue_declare(self.callback2, 
                              queue='findSegments')
        channel.basic_consume(self.callback,
                          queue='findSegments',
                          no_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        #channel.start_consuming()
    
    
    def callback2(self,channel):
        print(" queue declared" )    
        
        
    def callback(self,ch, method, properties, body):
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
        queueurl = os.environ.get('CLOUDAMQP_URL')
        #queueurl = 'amqp://_KUhGa2L:tDLeVGqDJCtkQmm7OBsGbiDhLsgL8h8s@scared-cowslip-30.bigwig.lshift.net:10242/ULoe2nXhmn9Y'
        params = pika.URLParameters(queueurl)
        sendConnection = pika.BlockingConnection(params)
        sendChannel = sendConnection.channel()
        returnData = {}
        returnData['segments'] = segments
        returnData['id'] = fileId
        message = json.dumps(returnData) 
        #sendChannel.queue_declare(self.callback2, 
        #                          queue='getSegments')
        
        sendChannel.basic_publish(exchange='',
                              routing_key='getSegments',
                              body=message)
        print(" [x] Sent  %r" % message)
        sendConnection.close()
        print(" [x] Received %r")    
    
    def run(self):
        # Parse CLODUAMQP_URL (fallback to localhost)
        print(" [x] start thread")
        url = os.environ.get('CLOUDAMQP_URL')
        #url = 'amqp://_KUhGa2L:tDLeVGqDJCtkQmm7OBsGbiDhLsgL8h8s@scared-cowslip-30.bigwig.lshift.net:10243/ULoe2nXhmn9Y'
        params = pika.URLParameters(url)
        params.socket_timeout = 5
        connection = pika.SelectConnection(parameters=params,
                                       on_open_callback=self.on_open)
        try:
            # Step #2 - Block on the IOLoop
            connection.ioloop.start()
            # Catch a Keyboard Interrupt to make sure that the connection is closed cleanly
        except KeyboardInterrupt:
            # Gracefully close the connection
            connection.close()
            # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
            connection.ioloop.start()
        return 



        



