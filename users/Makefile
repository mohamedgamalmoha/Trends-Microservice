test-install-requirements:
	pip install -r requirements-dev.txt

test-install-postgres:
	sudo apt update
	sudo apt install postgresql postgresql-contrib -y 

test-run-postgres:
	service postgresql start

test-staus-postgres:
	service postgresql status

test-setup-postgres:
	sudo -u postgres psql -c "CREATE USER users_test_db_user WITH PASSWORD '123456';"
	sudo -u postgres psql -c "CREATE DATABASE users_test_db;"
	sudo -u postgres psql -c "ALTER DATABASE users_test_db OWNER TO users_test_db_user;"
	sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE users_test_db TO users_test_db_user;"

test-teardown-postgres:
	sudo -u postgres psql -c "DROP DATABASE users_test_db;"
	sudo -u postgres psql -c "DROP USER users_test_db_user;"

test-stop-postgres:
	service postgresql stop

test-pre-run: test-install-requirements test-install-postgres test-run-postgres test-staus-postgres test-setup-postgres

test-post-run: test-teardown-postgres test-stop-postgres

test-run:
	pytest -v --tb=short --disable-warnings

test: test-pre-run test-run test-post-run

test-rerun: test-teardown-postgres test
