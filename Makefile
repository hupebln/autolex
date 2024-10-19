# grep the version from pyproject.toml, squeeze multiple spaces, delete double
#   and single quotes, get 3rd val. This command tolerates 
#   multiple whitespace sequences around the version number
VERSION := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)

# The name of the Docker image
IMAGE_NAME := "autolex"

# Build the Docker image
docker-build:
	docker build -t $(IMAGE_NAME):$(VERSION) .

docker-save: docker-build
	mkdir -p docker-save
	docker save $(IMAGE_NAME):$(VERSION) -o docker-save/$(IMAGE_NAME)_$(VERSION).tar.gz
