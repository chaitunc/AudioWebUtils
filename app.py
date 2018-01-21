from flask import Flask, request, jsonify
import audioBasicIO as aIO
import audioSegmentation as aS 

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# endpoint to create new user
@app.route("/getSegments", methods=["POST"])
def getSegments():
    print("received request")
    fileUrl = request.get_json()
    print(fileUrl)
    url = fileUrl['url']
    print(url)
    [Fs, x] = aIO.readAudioFileFromUrl(url)
    
    segments = aS.silenceRemoval(x, Fs, 0.020, 0.020, smoothWindow = 1.0, Weight = 0.3, plot = False)
    print(Fs)
    print(x)
    return jsonify(segments)

if __name__ == '__main__':
    app.run(debug=True)