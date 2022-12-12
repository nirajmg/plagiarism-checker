import os
from google.cloud import pubsub_v1
import json
from minio import Minio
import random
import string
from pathlib import Path

credentialsPath = 'key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()
subscriberPath = 'projects/plagiarism-368919/subscriptions/plagiarism-reports-sub'

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "GOOG7JBEJ7GU76OUS5HTT4RI")
secretKey = os.getenv('SECRET_KEY', "CV18bXT9flzceG2RVt6TN0AvgS13cuuR6wNfX4Nv")

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
    client.fget_object(bucket, file_name, local_file)
    f = open(f'{local_file}.html', 'w')

    headerText = "<!DOCTYPE html><html>"
    endText = "</html></body>"
    htmlText = ""
    with open(local_file) as fp:
        for line in fp:
            if not line.strip():continue
            checkPlagiarismResponse = json.loads(line)
            uniquePercent += checkPlagiarismResponse["uniquePercent"]
            count += 1
            details = checkPlagiarismResponse["details"]

            for idx in range(len(details)):
                if type(details[idx]) is dict:
                    if details[idx]['unique'] == "true":
                        queryHTML = "<p>" + details[idx]['query'] + "</p>"
                        htmlText += queryHTML
                    else:
                        queryHTML = "<p style='color:red'>" + \
                            details[idx]['query'] + "</p>"
                        htmlText += queryHTML
    plagiarismPercentage = f'The plagiarism percentage is {uniquePercent//count}%'
    fp.close()

    result = headerText + \
        f"<h2>{plagiarismPercentage}</h2>" + htmlText + endText
    f.write(result)
    f.close()

    user = file_name.split('/')[0]
    object_name = f'{user}/reports/{local_file}.html'
    result = client.fput_object(bucket, object_name, f'{local_file}.html')
    os.remove(f'{local_file}.html')
    os.remove(f'{local_file}')
    message.ack()

stream_pull_future = subscriber.subscribe(subscriberPath, callback=callback)
with subscriber:
    try:
        stream_pull_future.result()
    except TimeoutError:
        stream_pull_future.cancel()
        stream_pull_future.result()
