import os
from google.cloud import pubsub_v1
import json
from minio import Minio
import random
import string
from pathlib import Path

# credentialsPath = '/Users/ragulravisankar/Desktop/plagiarism-checker/plagiarism-check.privatekey.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath
credentialsPath = 'plagiarism-check.privatekey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()
subscriberPath = 'projects/plagiarism-368919/subscriptions/plagiarism-reports-sub'
fileName = (''.join(random.choices(string.ascii_letters, k=5)))+'.html'

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "")
secretKey = os.getenv('SECRET_KEY', "")
project = os.getenv('PROJECT', "plagiarism-368919")
subscription = os.getenv('SUBSCRIBER', "plagiarism-reports-sub")
subscriberPath = f'projects/{project}/subscriptions/{subscription}'

client = Minio(s3Src, access_key=secretId, secret_key=secretKey, secure=False)

def callback(message):
    uniquePercent = 0
    count = 0
    print(f'Received message: {message}')
    print(f'data: {message.data}')
    file_name = message.data.decode('utf-8')
    local_file = os.path.basename(file_name)
    client.fget_object(bucket, file_name,local_file)
    f = open(fileName,'w')
    local_file = 'temp.txt'
    # htmlText = "<!DOCTYPE html><html><head><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script></head><body>"
    headerText = "<!DOCTYPE html><html>"
    endText = "</html></body>"
    htmlText = ""
    with open(local_file) as fp:
        for line in fp:
            checkPlagiarismResponse = json.loads(line)
            uniquePercent+=checkPlagiarismResponse["uniquePercent"]
            count+=1
            details = checkPlagiarismResponse["details"]

            for idx in range(len(details)):
                if type(details[idx]) is dict:
                    if details[idx]['unique']=="true":
                        queryHTML = "<p>"+ details[idx]['query'] + "</p>"
                        htmlText+=queryHTML
                    else:
                        queryHTML = "<p style='color:red'>"+ details[idx]['query'] + "</p>"
                        htmlText+=queryHTML
    plagiarismPercentage = f'The plagiarism percentage is {uniquePercent//count}%'
    
    fp.close()
    
    result = headerText + f"<h2>{plagiarismPercentage}</h2>" + htmlText + endText
    f.write(result)
    f.close()
    object_name = fileName
    file_path = fileName
    result = client.fput_object(bucket, object_name, file_path,content_type="text/html") 
    os.remove(fileName)
    message.ack()

callback(None)
stream_pull_future = subscriber.subscribe(subscriberPath, callback = callback)

with subscriber:                                               
    try:
        stream_pull_future.result()                          
    except TimeoutError:
        stream_pull_future.cancel()                          
        stream_pull_future.result()

