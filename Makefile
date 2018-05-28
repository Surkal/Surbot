DOCKER = docker run -it --rm surbot

build:
	docker build -t surbot .

shell:
	docker run -it --rm -v $PWD:/src surbot /bin/bash

tests:
	$(DOCKER) python -m unittest
