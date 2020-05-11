default:
	@echo "See Makefile for available targets"

local-setup-environment:
	@echo "Installs virtual python environment with required dependencies using \
	pipenv package (https://pipenv-fork.readthedocs.io/en/latest/install.html#installing-pipenv)."
	@pipenv install --dev --skip-lock

local-run:
	@export $(grep -v '^#' .env.development | xargs)
	@docker-compose -f ./docker-elk/docker-compose.yml -f ./docker-elk/extensions/apm-server/apm-server-compose.yml up
	@pipenv run uvicorn main:app --reload

local-create-index:
	@echo "Adding logstash index to Kibana"
	@curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
		-H 'Content-Type: application/json' \
		-H 'kbn-version: 7.6.2' \
		-u elastic:changeme \
		-d '{"attributes":{"title":"logstash-*","timeFieldName":"@timestamp"}}' 
	@curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
		-H 'Content-Type: application/json' \
		-H 'kbn-version: 7.6.2' \
		-u elastic:changeme \
		-d '{"attributes":{"title":"apm-*","timeFieldName":"@timestamp"}}' 

local-run-tests:
	@pipenv run pytest

local-remove-all-dockerimages:
	@docker stop $(shell docker ps -a -q)
	@docker rm $(shell docker ps -a -q)
	@docker rmi $(shell docker images -a -q) --force
	@docker system prune --volumes

aws-deploy:
	@echo "The cloudformation templates has not yet been written"

