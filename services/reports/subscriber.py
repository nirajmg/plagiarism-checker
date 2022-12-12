import os
from google.cloud import pubsub_v1
import json
from minio import Minio
import random
import string

# credentialsPath = '/Users/ragulravisankar/Desktop/plagiarism-checker/plagiarism-check.privatekey.json'
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath
credentialsPath = 'plagiarism-check.privatekey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()
subscriberPath = 'projects/plagiarism-368919/subscriptions/plagiarism-reports-sub'
fileName = (''.join(random.choices(string.ascii_letters, k=5)))+'.html'

bucket = os.getenv('BUCKET', "plagiarism-ingestion1107")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "GOOG4342SX44CC4OM4OHFJ3B")
secretKey = os.getenv('SECRET_KEY', "NG8bZ0zVbcaIv4ic+U1TbtNrL3T+zkcNc6DdxdvT")
project = os.getenv('PROJECT', "plagiarism-368919")
subscription = os.getenv('SUBSCRIBER', "plagiarism-tasks-sub")
subscriberPath = f'projects/{project}/subscriptions/{subscription}'

client = Minio(s3Src, access_key=secretId, secret_key=secretKey, secure=False)

def callback(message):
    f = open(fileName,'w')
    decodedResponse = message.data.decode('utf-8')
    checkPlagiarismResponse = json.loads(decodedResponse)
    details = checkPlagiarismResponse["details"]
    htmlText = "<!DOCTYPE html><html><body>"
    # htmlText+= '<!-- CSS only --><link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel=\"stylesheet" integrity=\"sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin=\"anonymous">'
    
    for idx in range(len(details)):
        if details[idx]['unique']=="true":
            queryHTML = "<p>"+ details[idx]['query'] + "</p>"
            htmlText+=queryHTML
        else:
            queryHTML = "<p style='color:red'>"+ details[idx]['query'] + "</p>"
            htmlText+=queryHTML
    
    htmlText+="</html></body>"
    f.write(htmlText)
    f.close()
    object_name = fileName
    file_path = fileName
    result = client.fput_object(bucket, object_name, file_path,content_type="text/html") 
    os.remove(fileName)
    message.ack()

stream_pull_future = subscriber.subscribe(subscriberPath, callback = callback)

with subscriber:                                               
    try:
        stream_pull_future.result()                          
    except TimeoutError:
        stream_pull_future.cancel()                          
        stream_pull_future.result()

