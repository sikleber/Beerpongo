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

deploy: deploy-infrastructure


################ INFRASTRUCTURE ################

install-infrastructure:
	cd sys-src/infrastructure && pipenv sync

test-infrastructure: .install-dev-infrastructure
	cd sys-src/infrastructure && pipenv run pytest

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
# Todo flutter integration
install-frontend:
	cd sys-src/frontend

test-frontend: install-frontend
	cd sys-src/frontend

test-coverage-frontend: install-frontend
	cd sys-src/frontend


################ OTHER ################
create-python-layer-zip: install-backend
	cd sys-src/backend && pipenv requirements > requirements.txt && \
	pip install -r requirements.txt --upgrade --no-deps -t ./requirements/python && \
	pipenv run python scripts/zip_backend_layer.py
