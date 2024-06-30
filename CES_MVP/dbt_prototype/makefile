include .env
export

# variables
DBT_COMMAND_PREFIX := cd $(DBT_FOLDER) && pipenv run dbt

# phony targets
.PHONY: run debug compile clean db help setup docs reports

# targets
debug compile run:
	@echo "Run dbt"
	$(DBT_COMMAND_PREFIX) $@ --target $(DBT_TARGET)

clean:
	@echo "Clean dbt and db"
	$(DBT_COMMAND_PREFIX) $@ --target $(DBT_TARGET)
	@rm $(DATA_DIR)/$(DBT_TARGET).duckdb

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
	@echo "Spawning DuckDB"
	duckdb $(DATA_DIR)/$(DBT_TARGET).duckdb

# help message
help:
	@echo "Available tasks:"
	@echo "  db	        - Start dbt output duckdb"
	@echo "  debug		- Run dbt debug"
	@echo "  docs		- Build and serve dbt docs"
	@echo "  compile	- Run dbt compile"
	@echo "  transform	- Run dbt transform performing all the transformations"
	@echo "  reports	- Generate reports using evidence"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
