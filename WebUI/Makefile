VERSION=v1
DOCKERUSER=tejas1812

build:
	docker build --platform linux/amd64 -f Dockerfile -t WebUI .

push:
	docker tag WebUI $(DOCKERUSER)/WebUI:$(VERSION)
	docker push $(DOCKERUSER)/WebUI:$(VERSION)
	docker tag WebUI $(DOCKERUSER)/WebUI:latest
	docker push $(DOCKERUSER)/WebUI:latest
