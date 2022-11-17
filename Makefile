VERSION=v1
PROJECT=lab5-364722
DOCKERUSER=us-west3-docker.pkg.dev/lab5-364722/lab7
CLUSTER=cluster-1
REGION=us-west3-a

all: login

build: build-rest build-worker

build-worker:
	cd worker && gcloud builds submit --tag $(DOCKERUSER)/demucs-worker .

build-rest:
	cd rest && gcloud builds submit --tag $(DOCKERUSER)/demucs-rest .

login:
	gcloud container clusters get-credentials $(CLUSTER) --zone $(REGION) --project $(PROJECT)

infra: deploy-secret deploy-redis deploy-rest deploy-worker deploy-logs

deploy-redis:
	kubectl apply -f redis/

deploy-rest: 
	kubectl apply -f rest/infra/

deploy-worker:
	kubectl apply -f worker/infra/

deploy-logs:
	kubectl apply -f logs/

deploy-secret:
	kubectl create secret generic credentials --from-env-file .env

lb:
	gcloud container clusters update $(CLUSTER) --update-addons=HttpLoadBalancing=ENABLED  --zone $(REGION)

requirements:
	cd worker && python3 -m pigar -p requirements.txt -P .
	cd rest && python3 -m pigar -p requirements.txt -P .

port-forward:
	kubectl port-forward --address 0.0.0.0 service/redis 6379:6379 &
	kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &
	kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001 &
