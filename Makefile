.PHONY : help install update test lint clean build publish all

all: test

# Install project dependencies
install:
	poetry install

# Update project dependencies
update:
	poetry update

# Run project tests
test:
	poetry run pytest --cov-report xml --cov=athena_federation


watch:
	poetry run ptw . --now

# Lint code using flake8
lint:
	black .
	flake8

# Clean up generated files
clean:
	poetry run rm -rf dist build

# Build project distribution
build: lint
	poetry build

# Publish project to PyPI
publish: build
	poetry publish


## Docker Commands

docker: docker-build docker-run lambda-ping

# Verify Docker is running

docker-status:
	docker ps

# Build Docker image
docker-build:
	docker build -t athena-federation .

docker-debug:
	docker build -t athena-federation . --no-cache --build-arg DEBUG=true

docker-poetry-config:
	poetry config virtualenvs.in-project true --local

# Run Docker container

docker-run: docker-build
	docker run -it -p 5000:5000 athena-federation

# Run Docker container in detached mode

docker-detached:
	docker run -d -p 5000:5000 athena-federation

# Stop Docker container

docker-stop:
	docker stop $(docker ps -a -q)


# Ping lambda

lambda-ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "PingRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'

lambda-list-schemas:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "ListSchemasRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'
