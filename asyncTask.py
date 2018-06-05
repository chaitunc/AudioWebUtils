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

import threading  
class AsyncTask(threading.Thread):
    def __init__(self, fileId, url):
        super(AsyncTask,self).__init__()
        self.fileId = fileId
        self.url = url
    def run(self):
        print(len(self.url))
        [Fs, x] = aIO.readAudioFileFromUrl(self.url)
        ShortTermFeatures = aS.silenceRemoval(x, Fs, 0.020, 0.020, smoothWindow = 1.0, Weight = 0.3, plot = False)
        [SVM, MEANSS, STDSS] = aS.step2(ShortTermFeatures)
        MaxIdx = aS.step3(ShortTermFeatures, MEANSS, STDSS, SVM, 0.020, smoothWindow = 1.0, Weight = 0.3)
        segments = aS.step4(MaxIdx,0.020)
        print(segments)
        outputFile = open(self.fileId,"w") 
        outputFile.write(json.dumps(segments))
        outputFile.close()
        return 
