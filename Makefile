VERSION=v1
PROJECT_ID=plagiarism-368919
PROJECT_NUMBER=$(shell gcloud projects list --filter="project_id:$(PROJECT_ID)" --format='value(project_number)')
SERVICE_ACCOUNT=$(shell gsutil kms serviceaccount -p $(PROJECT_NUMBER))


BUCKET=plagiarism-ingestion
CLOUD_FUNC_NAME=storage-trigger-function
TOPIC=plagiarism-tasks
CLUSTER=plagiarism-cluster
REGION=us-west3

all: login clean build infra

login:
	gcloud auth login && gcloud config set project $(PROJECT_ID)

build: build-cloudfunc

infra: deploy-bucket deploy-cloudfunc deploy-pubsub

build-cloudfunc:
	cd functions/storage && pip3 install -r requirements.txt 

build-frontend:
	cd services/frontend && pip3 install -r requirements.txt 

deploy-bucket:
	gsutil mb -l $(REGION) gs://$(BUCKET)
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
	--member serviceAccount:$(SERVICE_ACCOUNT) \
	--role roles/pubsub.publisher --role roles/eventarc.eventReceiver

deploy-cloudfunc:
	gcloud functions deploy $(CLOUD_FUNC_NAME) --gen2 \
	--runtime=python310 \
	--region=$(REGION) \
	--source=./functions/storage \
	--entry-point=process_trigger \
	--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
	--trigger-event-filters="bucket=$(BUCKET)"

deploy-pubsub:
	gcloud pubsub topics create $(TOPIC) --message-retention-duration=1d


clean: 
	gcloud storage rm --recursive gs://$(BUCKET)/
	gcloud pubsub topics delete $(TOPIC)
	gcloud functions delete $(CLOUD_FUNC_NAME) --gen2 --region=$(REGION)
	helm delete postgresql

helm:
	helm install postgresql infra/postgresql
	# all services will be deployed here 


requirements:
	cd services/frontend && python3 -m pigar -p requirements.txt -P .
	