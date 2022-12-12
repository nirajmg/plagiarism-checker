import os
from minio import Minio
from google.cloud import pubsub_v1
import PyPDF2
from flask_login import login_required, current_user

credentialsPath = 'plagiarism-check.privatekey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentialsPath

subscriber = pubsub_v1.SubscriberClient()
subscriberPath = 'projects/plagiarism-368919/subscriptions/plagiarism-tasks-sub-originalfile'
fileName = (''.join(random.choices(string.ascii_letters, k=5)))+'.html'

bucket = os.getenv('BUCKET', "plagiarism-ingestion1107")
s3Src = os.getenv('S3_SRC', "storage.googleapis.com")
secretId = os.getenv('SECRET_ID', "GOOG4342SX44CC4OM4OHFJ3B")
secretKey = os.getenv('SECRET_KEY', "NG8bZ0zVbcaIv4ic+U1TbtNrL3T+zkcNc6DdxdvT")
project = os.getenv('PROJECT', "plagiarism-368919")
subscription = os.getenv('SUBSCRIBER', "plagiarism-tasks-sub")
subscriberPath = f'projects/{project}/subscriptions/{subscription}'



client = Minio(s3Src, access_key=secretId, secret_key=secretKey)

url = 'https://www.check-plagiarism.com/apis/checkPlag'
key = '422ccf1360520da2957f319bdd10246f'

x = requests.post(url, json = myobj)

def callback(message):
	print(f'Received message: {message}')
	print(f'data: {message.data}')
	blob_name = message.data.decode('utf-8')
	storage_client = storage.Client()
	bucket_access = storage_client.bucket(bucket)
	blob = bucket_access.blob(blob_name)
	
	pdffile = open(blob, mode='rb')
	pdfdoc = PyPDF2.PdfFileReader(pdffile)

	file_key = hashlib.md5(open(blob,'rb').read()).hexdigest()
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

		output_file=dict()
		output['id'] =file_key
		output['data']=r.text

		# Serializing json
		json_object = json.dumps(output_file, indent=4)
 

		object_name = f'{current_user.email}/files/{secure_filename(file_key)}'
		result = client.put_object(bucket, object_name, json_object, length=-1, part_size=10*1024*1024,) 
		flash(f'{file_key} was successfully uploaded', 'success')



		




	
# subscribe method provides an asynchronous interface for processing its callback
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
with subscriber:                                           # wrap subscriber in a 'with' block to automatically call close() when done
    try:
        streaming_pull_future.result()                          # going without a timeout will wait & block indefinitely
    except TimeoutError:
        streaming_pull_future.cancel()                          # trigger the shutdown
        streaming_pull_future.result()

