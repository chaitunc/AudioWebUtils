import audioBasicIO as aIO
import audioSegmentation as aS 
import audioTrainTest as aT
import glob, sys, os
'''
aT.featureAndTrain(["C:\\workspaces_python\pyAudioAnalysis\data\satvik","C:\\workspaces_python\pyAudioAnalysis\data\other"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "svm", "svm5Classes")
aT.featureAndTrain(["C:\\workspaces_python\pyAudioAnalysis\data\satvik","C:\\workspaces_python\pyAudioAnalysis\data\other"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "knn", "knnClasses")
aT.featureAndTrain(["C:\\workspaces_python\pyAudioAnalysis\data\satvik","C:\\workspaces_python\pyAudioAnalysis\data\other"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "extratrees", "extratreesClasses")
aT.featureAndTrain(["C:\\workspaces_python\pyAudioAnalysis\data\satvik","C:\\workspaces_python\pyAudioAnalysis\data\other"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "gradientboosting", "gb5Classes")
aT.featureAndTrain(["C:\\workspaces_python\pyAudioAnalysis\data\satvik","C:\\workspaces_python\pyAudioAnalysis\data\other"], 1.0, 1.0, aT.shortTermWindow, aT.shortTermStep, "randomforest", "rf5Classes")



cls = aS.speakerDiarization("C:\\workspaces_python\\pyAudioAnalysis\\data\\test\\20180116_190208.wav", 0, PLOT=True)
print (cls)



def getWavFilesFromFolder(dirPath):
    files_grabbed = []
    files_grabbed.extend(glob.glob(dirPath))
    return files_grabbed


files = getWavFilesFromFolder("C:\\workspaces_python\\pyAudioAnalysis\\data\\test\\*.wav")
for f in files:
    [Result, P, classNames] = aT.fileClassification(f, "svm5Classes","svm")
    print(" svm " + f)
    print( Result )
    print ( P )
    [Result, P, classNames] = aT.fileClassification(f, "knnClasses","knn")
    print(" knn " + f)
    print( Result )
    print ( P )
    [Result, P, classNames] = aT.fileClassification(f, "extratreesClasses","extratrees")
    print(" extratrees " + f)
    print( Result )
    print ( P )
    [Result, P, classNames] = aT.fileClassification(f, "gb5Classes","gradientboosting")
    print(" gradientboosting " + f)
    print( Result )
    print ( P )
    [Result, P, classNames] = aT.fileClassification(f, "rf5Classes","randomforest")
    print(" randomforest " + f)
    print( Result )
    print ( P )
    '''


[Fs, x] = aIO.readAudioFile("C:\\Users\\Mundhu.mp3")
segments = aS.silenceRemoval(x, Fs, 0.020, 0.020, smoothWindow = 1.0, Weight = 0.3, plot = False)
print(segments)