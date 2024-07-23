DOCKFILE=./Dockerfile
IMAGE=ocpp:1.0
CONTAINER=ocppCentral
NETW=--network host

venv:
	./VENV.sh

compile:
	pyinstaller --onefile Central.py --name Central.x --add-data ".venv/lib/python3.12/site-packages/ocpp/v16/schemas:ocpp/v16/schemas" \
		--add-data ".venv/lib/python3.12/site-packages/ocpp/v201/schemas:ocpp/v201/schemas"

build: dist/Central.x
	sudo docker build -f $(DOCKFILE) -t $(IMAGE) .

run:
	-sudo docker kill $(CONTAINER)
	sudo docker run --rm --name $(CONTAINER) $(NETW) $(IMAGE) &

kill:
	-sudo docker kill $(CONTAINER)

clean:
	-rm -r dist build .venv
