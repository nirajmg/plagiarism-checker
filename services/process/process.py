import os
from minio import Minio
from google.cloud import pubsub_v1
import os
import requests 
import docx 
import pdfplumber 

credentialsPath = 'key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()

bucket = os.getenv('BUCKET', "plagiarism-ingestion")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "")
secretKey = os.getenv('SECRET_KEY', "")
project = os.getenv('PROJECT', "plagiarism-368919")
subscription = os.getenv('SUBSCRIBER_RAW', "plagiarism-raw-sub")
subscriberPath = f'projects/{project}/subscriptions/{subscription}'



client = Minio(s3Src, access_key=secretId, secret_key=secretKey)

url = os.getenv('PL_URL', "https://www.check-plagiarism.com/apis/checkPlag")
key = os.getenv('API_KEY', "")


def callback(message):
	print(f'Received message: {message}')
	print(f'data: {message.data}')
	file_name = message.data.decode('utf-8')
	
	local_file = os.path.basename(file_name)
	client.fget_object(bucket, file_name,local_file)
	json_file = open(f'{local_file}.json', 'a+')

	if local_file.endswith('.docx'):
		doc = docx.Document(local_file)
		for para in doc.paragraphs:
			form_data= dict()
			if para.text=='': continue
			form_data['key'] = key
			form_data['data'] =para.text
			r = requests.post(url, data=form_data)
			if r.status_code==200 :
				json_file.write(r.content.decode("utf-8"))
				json_file.write('\n')
	elif local_file.endswith('.pdf'):
		pdfdoc= pdfplumber.open(local_file)
		for i in range(len(pdfdoc.pages)):
			current_page = pdfdoc.pages[i]
			text_to_be_sent= current_page.extract_text()
			form_data= dict()
			form_data['key'] = key
			form_data['data'] =text_to_be_sent
			r = requests.post(url, data=form_data)
			json_file.write(r.content.decode('utf-8'))
			json_file.write('\n')
	else: 
		return 

	user=file_name.split('/')[0]
	object_name = f'{user}/raw/{local_file}'
	result = client.fput_object(bucket, object_name, f'{local_file}.json') 
	os.remove(local_file)
	os.remove(f'{local_file}.json')
	message.ack()


#subscribe method provides an asynchronous interface for processing its callback
streaming_pull_future = subscriber.subscribe(subscriberPath, callback=callback)
with subscriber:                                           # wrap subscriber in a 'with' block to automatically call close() when done
    try:
        streaming_pull_future.result()                          # going without a timeout will wait & block indefinitely
    except TimeoutError:
        streaming_pull_future.cancel()                          # trigger the shutdown
        streaming_pull_future.result()

