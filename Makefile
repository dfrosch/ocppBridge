#DOCKFILE=./Dockerfile
#IMAGE=ocpp:1.0

DOCKFILE=./Dockerfile.distroless
IMAGE=ocppdebian:1.0

CONTAINER=ocppCentral
NETW=--network host

venv:
	./VENV.sh

compile:
	pyinstaller --onefile Central.py --name Central.x --add-data ".venv/lib/python3.12/site-packages/ocpp/v16/schemas:ocpp/v16/schemas" \
		--add-data ".venv/lib/python3.12/site-packages/ocpp/v201/schemas:ocpp/v201/schemas"

buildx:
	sudo docker build -f $(DOCKFILE) -t $(IMAGE) .

run:
	-sudo docker kill $(CONTAINER)
	sudo docker run --rm --name $(CONTAINER) $(NETW) $(IMAGE) &
	sudo docker ps

kill:
	-sudo docker kill $(CONTAINER)

clean:
	-rm -r dist build .venv

inspect:
	sudo docker create --name="tmp" $(IMAGE)
	sudo docker export tmp | tar t
	sudo docker rm tmp
