#DOCKFILE=./Dockerfile
#IMAGE=ocpp:1.0

DOCKFILE=./Dockerfile.distroless
IMAGE=ocppdebian:1.0

CONTAINER=ocppCentral
#NETW=--network host
NETW=-p 9000:9000

venv:
	./VENV.sh

compile:
	pyinstaller --onefile Central.py --name Central.x --add-data ".venv/lib/python3.12/site-packages/ocpp/v16/schemas:ocpp/v16/schemas" \
		--add-data ".venv/lib/python3.12/site-packages/ocpp/v201/schemas:ocpp/v201/schemas"

buildx:
	docker build -f $(DOCKFILE) -t $(IMAGE) .

run:
	-docker kill $(CONTAINER)
	sleep 2
	docker run --rm --name $(CONTAINER) $(NETW) $(IMAGE) &
	sleep 2
	docker ps

kill:
	-docker kill $(CONTAINER)

clean:
	-rm -r dist build .venv

inspect:
	docker create --name="tmp" $(IMAGE)
	docker export tmp | tar t
	docker rm tmp

logs:
	docker logs -f $(CONTAINER)

# Kubernetes minikub deployment
deploy:
	eval $(minikube -p minikube docker-env)
	docker build -f $(DOCKFILE) -t $(IMAGE) .
	kubectl apply -f ocppBridge-deployment.yml
	kubectl expose deployment ocppbridge-deployment --type=NodePort --port=9000
