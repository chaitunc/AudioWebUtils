from __future__ import print_function
from tempfile import TemporaryFile, NamedTemporaryFile
from flask import Flask, request, jsonify
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from io import BytesIO
from oauth2client.client import AccessTokenCredentials
from flask import stream_with_context, request, Response

import audioBasicIO as aIO
import audioSegmentation as aS 
import httplib2
import os


app = Flask(__name__)

@app.route("/")
def hello():
     return "Hello World!"

# endpoint to create new user
@app.route("/getSegments", methods=["POST"])
def getSegments():
    print("received request")
    fileUrl = request.get_json()
    fileId = fileUrl['id']
    accessToken = fileUrl['accessToken']
    credentials = AccessTokenCredentials(accessToken, 'my-user-agent/1.0')
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = discovery.build('drive', 'v2', http=http)
    url=service.files().get_media(fileId=fileId).execute()
    
    def silentSegments(url):
        [Fs, x] = aIO.readAudioFileFromUrl(url)
        ShortTermFeatures = aS.silenceRemoval(x, Fs, 0.020, 0.020, smoothWindow = 1.0, Weight = 0.3, plot = False)
        print("so far completed..")
        yield jsonify(Fs).data
        [SVM, MEANSS, STDSS] = aS.step2(ShortTermFeatures)
        MaxIdx = aS.step3(ShortTermFeatures, MEANSS, STDSS, SVM, 0.020, smoothWindow = 1.0, Weight = 0.3)
        segments = aS.step4(MaxIdx,0.020)
        print(segments)
        yield jsonify(results = segments).data
    
    
    return Response(stream_with_context(silentSegments(url)), content_type='application/json')




if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)