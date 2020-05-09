default:
	@echo "See Makefile for available targets"

local-setup-environment:
	@echo "Installs virtual python environment with required dependencies using \
	pipenv package (https://pipenv-fork.readthedocs.io/en/latest/install.html#installing-pipenv)."
	@pipenv install --dev --skip-lock

local-run:
	@docker-compose -f elastic-apm/docker-compose.yml up -d
	@pipenv run uvicorn main:app --reload

local-run-tests:
	@pipenv run pytest

aws-deploy:
	@echo "The cloudformation templates has not yet been written"

