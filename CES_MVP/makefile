include .env
export

# variables
DBT_COMMAND_PREFIX := cd $(DBT_FOLDER) && pipenv run dbt

# phony targets
.PHONY: transform debug compile db help setup docs reports

# targets
transform:
	@echo "Transforming data"
	$(DBT_COMMAND_PREFIX) run --target $(DBT_TARGET)

debug compile:
	@echo "Debugging dbt"
	$(DBT_COMMAND_PREFIX) $@ --target $(DBT_TARGET)

setup:
	@echo "🏗️ Setting up project\n"
	@echo "💡 Make sure to have nvm installed and run 'nvm use' to use the correct node version\n"
	pipenv install --dev
	npm --prefix $(DBT_FOLDER)/reports install

reports:
	@echo "Generate reports using evidence.dev"
	npm --prefix $(DBT_FOLDER)/reports run sources
	npm --prefix $(DBT_FOLDER)/reports run dev

docs:
	@echo "Generating documentation"
	$(DBT_COMMAND_PREFIX) docs generate --target $(DBT_TARGET)
	$(DBT_COMMAND_PREFIX) docs serve --target $(DBT_TARGET)

db:
	@echo "Spawning DuckDB using init.sql"
	duckdb $(DATA_DIR)/$(DBT_TARGET).duckdb

# help message
help:
	@echo "Available tasks:"
	@echo "  db		- Start dbt output duckdb"
	@echo "  debug		- Run dbt debug"
	@echo "  compile	- Run dbt compile"
	@echo "  transform	- Run dbt transform performing all the transformations"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
