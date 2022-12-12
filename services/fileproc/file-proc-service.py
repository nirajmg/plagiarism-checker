import os
from minio import Minio
from google.cloud import pubsub_v1
import PyPDF2
import os
from google.cloud import pubsub_v1
import json
from minio import Minio
import random
import string
import requests 

credentialsPath = 'plagiarism-check.privatekey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "GOOG7JBEJ7GU76OUS5HTT4RI")
secretKey = os.getenv('SECRET_KEY', "CV18bXT9flzceG2RVt6TN0AvgS13cuuR6wNfX4Nv")
project = os.getenv('PROJECT', "plagiarism-368919")
subscription = os.getenv('SUBSCRIBER_RAW', "plagiarism-raw-sub")
subscriberPath = f'projects/{project}/subscriptions/{subscription}'



client = Minio(s3Src, access_key=secretId, secret_key=secretKey)

url = os.getenv('PL_URL', "")
key = os.getenv('API_KEY', "")


def callback(message):
	print(f'Received message: {message}')
	print(f'data: {message.data}')
	file_name = message.data.decode('utf-8')
	
	local_file = os.path.basename(file_name)
	client.fget_object(bucket, file_name,local_file)
	
	pdffile = open(local_file, mode='rb')
	pdfdoc = PyPDF2.PdfFileReader(pdffile)

	json_file = open(f'{local_file}.json', 'a+')

	for i in range(pdfdoc.numPages):
		current_page = pdfdoc.getPage(i)
		print("===================")
		print("Page NO:" + str(i + 1))
		print("===================")
		text_to_be_sent= current_page.extractText()
		form_data= dict()
		form_data['key'] = key
		form_data['data'] =text_to_be_sent

		r = requests.post(url, data=form_data)
		json_file.write(r.text)

	
	user=file_name.split('/')[0]
	object_name = f'{user}/raw/{local_file}'
	result = client.fput_object(bucket, object_name, json_file) 
	os.remove(json_file)


# subscribe method provides an asynchronous interface for processing its callback
streaming_pull_future = subscriber.subscribe(subscriberPath, callback=callback)
with subscriber:                                           # wrap subscriber in a 'with' block to automatically call close() when done
    try:
        streaming_pull_future.result()                          # going without a timeout will wait & block indefinitely
    except TimeoutError:
        streaming_pull_future.cancel()                          # trigger the shutdown
        streaming_pull_future.result()

