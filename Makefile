export PYTHONPATH = src
MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
BASE_DIR := $(dir $(MAKEFILE_PATH))
SRC_DIR := $(BASE_DIR)src
BIN_DIR := $(BIN_DIR)bin
PYTHON := /usr/local/bin/python3.12

default: help

clear-screen:  # Clears the screen
	clear

shell:  # Opens a shell in the api container
	docker exec -it api /bin/bash

dev-up: dev-down # builds and fires up the dev docker environment
	docker-compose -f docker-compose.yaml up --build

dev-down:  # Shuts down the docker dev environment
	docker-compose down

logs:  # Follows docker logs
	docker logs --follow api

stripe-forwarder:  # Starts an event forwarder from Stripe to the local dev environment
	stripe listen --forward-to localhost:8000 --use-configured-webhooks

test: clear-screen venv  # Runs all tests
# 	docker-compose exec api pytest --cov=wj --cov-report term-missing --cov-report=html:doc/coverage
	. venv/bin/activate; pytest --cov=ninety_seven_things --cov-report term-missing --cov-report=html:doc/coverage -W ignore::DeprecationWarning

test-wip: clear-screen venv  # Runs selected tests
	. venv/bin/activate; pytest -m wip -W ignore::DeprecationWarning
	#docker-compose exec api pytest -v -m wip -W ignore::DeprecationWarning

prune:  # Prunes old docker data
	docker system prune -a -f

localtunnel:  # Creates a localtunnel
	pushd /tmp; lt --port 80 --subdomain whosjammin

clean-venv:  # Removes the existing venv
	rm -rf venv

venv: venv/touchfile  # Creates a new venv

venv/touchfile:
	test -d venv || virtualenv venv -p $(PYTHON)
	. venv/bin/activate; pip install --upgrade pip; pip install -U -r requirements/base.txt -r requirements/development.txt
	touch venv/touchfile

vulture:  # Runs vulture
	vulture src

pyright:  # Runs pyright
	pyright

pylint:  # Runs pylint
	pylint src/ninety_seven_things

ruff:  # Runs ruff
	ruff src

isort:  # Runs isort
	isort src

validate-openapi:
	openapi-generator validate -i http://localhost:8000/api/v1/openapi.json

format: clear-screen  # Format files using ruff and isort
	isort src
	isort tests
	ruff format src
	ruff format tests

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done
