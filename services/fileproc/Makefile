VERSION=v5
DOCKERUSER=tejas1812

build:
	docker build  --platform linux/amd64 -f Dockerfile -t fileproc .
push:
	docker tag fileproc $(DOCKERUSER)/fileproc/:$(VERSION)
	docker push $(DOCKERUSER)/fileproc:$(VERSION)
	docker tag fileproc $(DOCKERUSER)/fileproc:latest
	docker push $(DOCKERUSER)/fileproc:latest
