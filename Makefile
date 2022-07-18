################ ALL ################
prepare:
	python -m ensurepip --upgrade
	python -m pip install --upgrade pip
	python -m pip install --upgrade pipenv


install: install-infrastructure install-backend install-frontend

test: test-infrastructure test-backend test-frontend

test-coverage: test-coverage-infrastructure test-coverage-backend test-coverage-frontend

formatting-checks: formatting-checks-infrastructure formatting-checks-backend

format: format-infrastructure format-backend

deploy: deploy-infrastructure build-docker-frontend

start: start-docker-frontend


################ INFRASTRUCTURE ################

install-infrastructure:
	cd sys-src/infrastructure && pipenv sync

test-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run pytest

test-coverage-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run pytest --cov

formatting-checks-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run flake8 . && pipenv run black . --check && pipenv run isort . --check

format-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run black . && pipenv run isort .

deploy-infrastructure: install-infrastructure test-infrastructure
	cd sys-src/infrastructure && cdk deploy -c config=$(CONFIG) --profile $(PROFILE) $(STACK)

destroy-infrastructure: install-infrastructure
	cd sys-src/infrastructure && cdk destroy -c config=$(CONFIG) --require-approval never --profile $(PROFILE) $(STACK)

.install-dev-infrastructure:
	cd sys-src/infrastructure && pipenv sync --dev


################ BACKEND ################

install-backend:
	cd sys-src/backend && pipenv sync

test-backend: .install-dev-backend
	cd sys-src/backend && pipenv run pytest

test-coverage-backend: .install-dev-backend
	cd sys-src/backend && pipenv run pytest --cov

.install-dev-backend:
	cd sys-src/backend && pipenv sync --dev

formatting-checks-backend: .install-dev-backend
	cd sys-src/backend && pipenv run flake8 . && pipenv run black . --check && pipenv run isort . --check

format-backend: .install-dev-backend
	cd sys-src/backend && pipenv run black . && pipenv run isort .


################ FRONTEND ################
install-frontend:
	cd sys-src/frontend/beerpongo-react && npm install

test-frontend: install-frontend
	cd sys-src/frontend/beerpongo-react && npm run test -- --watchAll=false

test-coverage-frontend: install-frontend
	cd sys-src/frontend/beerpongo-react && npm run test -- --coverage --watchAll=false

start-frontend: install-frontend
	cd sys-src/frontend/beerpongo-react && npm run start

build-docker-frontend:
	cd sys-src/frontend/beerpongo-react && docker build -t beerpongo-webapp:latest .

start-docker-frontend: build-docker-frontend
	cd sys-src/frontend/beerpongo-react && docker run -d -p 80:80 beerpongo-webapp:latest

