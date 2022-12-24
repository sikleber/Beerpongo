################ ALL ################
prepare:
	python -m pip install --upgrade pip
	python -m pip install --upgrade pipenv


install: install-infrastructure install-backend install-frontend

test: test-infrastructure test-backend # test-frontend

test-coverage: test-coverage-infrastructure test-coverage-backend test-coverage-frontend

formatting-checks: formatting-checks-infrastructure formatting-checks-backend

format: format-infrastructure format-backend

deploy: deploy-infrastructure build-docker-frontend

start: start-docker-frontend


################ INFRASTRUCTURE ################

install-infrastructure:
	cd sys-src/infrastructure && pipenv sync

test-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run mypy cdk && pipenv run pytest

test-coverage-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run pytest --cov

formatting-checks-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run pflake8 . && pipenv run black . --check && pipenv run isort . --check

format-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run black . && pipenv run isort .

deploy-infrastructure: install-infrastructure create-python-layer-zip test-infrastructure
	cd sys-src/infrastructure && pipenv run cdk deploy -c config=$(CONFIG) --profile $(PROFILE) $(STACK) --require-approval never

destroy-infrastructure: install-infrastructure
	cd sys-src/infrastructure && pipenv run cdk destroy -c config=$(CONFIG) --require-approval never --profile $(PROFILE) $(STACK)

.install-dev-infrastructure:
	cd sys-src/infrastructure && pipenv sync --dev


################ BACKEND ################

install-backend:
	cd sys-src/backend && pipenv sync

test-backend: .install-dev-backend
	cd sys-src/backend && pipenv run mypy src && pipenv run pytest

test-coverage-backend: .install-dev-backend
	cd sys-src/backend && pipenv run pytest --cov

.install-dev-backend:
	cd sys-src/backend && pipenv sync --dev

formatting-checks-backend: .install-dev-backend
	cd sys-src/backend && pipenv run pflake8 . && pipenv run black . --check && pipenv run isort . --check

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


################ OTHER ################
create-python-layer-zip: install-backend
	cd sys-src/backend && pipenv requirements > requirements.txt && \
	pip install -r requirements.txt --no-deps --python-version 3.9 --platform manylinux2014_x86_64 --implementation cp --only-binary=:all: --upgrade -t ./requirements/python && \
	pipenv run python scripts/zip_backend_layer.py
