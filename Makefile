DOCKER = docker run -it --rm surbot

build:
	docker build -t surbot .

shell:
	docker run -it --rm -v $PWD:/src surbot /bin/bash

test:
	$(DOCKER) python -m unittest -v

coverage:
	$(DOCKER) coverage run -m unittest
