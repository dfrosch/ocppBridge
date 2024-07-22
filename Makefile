DOCKFILE=./Dockerfile
IMAGE=ocpp:1.0
CONTAINER=ocppCentral

venv:
	python3 -m venv .venv
	source .venv/bin/activate
	python3 -m pip install -r requirements.txt

compile:
	pyinstaller --onefile Central.py --name Central.x

build: dist/Central.x
	sudo docker build -f $(DOCKFILE) -t $(IMAGE) .

run:
	-sudo docker kill $(CONTAINER)
	sudo docker run --rm --name $(CONTAINER) $(IMAGE) &

kill:
	-sudo docker kill $(CONTAINER)

clean:
	-rm -r dist build
