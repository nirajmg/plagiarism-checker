VERSION=v1
PROJECT_ID=plagiarism-368919   
PROJECT_NUMBER=$(shell gcloud projects list --filter="project_id:$(PROJECT_ID)" --format='value(project_number)')
SERVICE_ACCOUNT=$(shell gsutil kms serviceaccount -p $(PROJECT_NUMBER))
DOCKERUSER=us-west3-docker.pkg.dev/plagiarism-368919/plagiarism
BUCKET=plagiarism-ingestion
CLOUD_FUNC_NAME=storage-trigger-function
TOPIC_RAW=plagiarism-raw
TOPIC_REPORTS=plagiarism-reports
SUBSCRIBER_RAW=plagiarism-raw-sub
SUBSCRIBER_REPORTS=plagiarism-reports-sub
CLUSTER=cluster-1
REGION=us-west3

all: login cluster clean build infra

login:
	gcloud auth login && gcloud config set project $(PROJECT_ID)

cluster:
	gcloud container clusters create $(CLUSTER) --region=$(REGION)

build: build-cloudfunc build-services

infra: deploy-pubsub deploy-bucket deploy-cloudfunc 

build-cloudfunc:
	cd functions/storage && pip3 install -r requirements.txt 

build-services:
	cd services/frontend && gcloud builds submit --tag $(DOCKERUSER)/frontend .
	cd services/process && gcloud builds submit --tag $(DOCKERUSER)/process .
	cd services/reports && gcloud builds submit --tag $(DOCKERUSER)/reports . 

deploy-bucket:
	gsutil mb -l $(REGION) gs://$(BUCKET)
 	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
 	--member serviceAccount:$(SERVICE_ACCOUNT) \
 	--role roles/pubsub.publisher --role roles/eventarc.eventReceiver

deploy-cloudfunc:
	gcloud services enable run.googleapis.com
	gcloud services enable eventarc.googleapis.com
	gcloud functions deploy $(CLOUD_FUNC_NAME) --gen2 \
	--runtime=python310 \
	--region=$(REGION) \
	--source=./functions/storage \
	--entry-point=process_trigger \
	--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
	--trigger-event-filters="bucket=$(BUCKET)" \
 	

deploy-pubsub:
	gcloud pubsub topics create $(TOPIC_RAW) --message-retention-duration=1d && \
	gcloud pubsub subscriptions create $(SUBSCRIBER_RAW) --topic=$(TOPIC_RAW)
	gcloud pubsub topics create $(TOPIC_REPORTS) --message-retention-duration=1d && \
	gcloud pubsub subscriptions create $(SUBSCRIBER_REPORTS) --topic=$(TOPIC_REPORTS)

clean: 
	gcloud storage rm --recursive gs://$(BUCKET)/
	gcloud pubsub topics delete $(TOPIC_RAW)
	gcloud pubsub subscriptions delete $(SUBSCRIBER_RAW)
	gcloud pubsub topics delete $(TOPIC_REPORTS)
	gcloud pubsub subscriptions delete $(SUBSCRIBER_REPORTS)
	gcloud functions delete $(CLOUD_FUNC_NAME) --gen2 --region=$(REGION)
	gcloud container clusters delete $(CLUSTER) --region=$(REGION)
	helm delete postgresql

helm:
	helm install postgresql infra/postgresql
	# all services will be deployed here 

requirements:
	cd services/frontend && python3 -m pigar -p requirements.txt -P .

deploy-cluster:
	gcloud container clusters get-credentials $(CLUSTER) --zone us-west3-a --project $(PROJECT_ID)
	gcloud container clusters update $(CLUSTER) --update-addons=HttpLoadBalancing=ENABLED  --zone us-west3-a
	kubectl create secret generic credentials --from-env-file .env
	helm install postgresql infra/postgresql
	kubectl apply -f infra/frontend
	#kubectl apply -f infra/reports