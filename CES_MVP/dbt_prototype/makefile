include .env
export

# variables
DBT_COMMAND_PREFIX := cd $(DBT_FOLDER) && pipenv run dbt

# phony targets
.PHONY: run debug compile clean db help setup docs reports extract

# targets
setup:
	@echo "🏗️ Setting up project\n"
	@echo "💡 Make sure to have nvm installed and run 'nvm use' to use the correct node version\n"
	pipenv install --dev
	npm --prefix $(DBT_FOLDER)/reports install

generate:
	@echo "Extract data and generate .csv report"
	make check
	make extract
	make build
	make export_csv

ui:
	@echo "Extract data and generate .csv report"
	make check
	make extract
	make build
	make reports

clean:
	@echo "Clean dbt and db"
	$(DBT_COMMAND_PREFIX) $@ --target $(DBT_TARGET)
	@rm $(DATA_DIR)/$(DBT_TARGET).duckdb || true

debug compile run build:
	@echo "Run dbt"
	$(DBT_COMMAND_PREFIX) $@ --target $(DBT_TARGET)

reports:
	@echo "Start evidence.dev ui"
	npm --prefix $(DBT_FOLDER)/reports run sources
	npm --prefix $(DBT_FOLDER)/reports run dev

docs:
	@echo "Generating documentation"
	$(DBT_COMMAND_PREFIX) docs generate --target $(DBT_TARGET)
	$(DBT_COMMAND_PREFIX) docs serve --target $(DBT_TARGET)

db:
	@echo "Spawning DuckDB"
	duckdb $(DATA_DIR)/$(DBT_TARGET).duckdb

extract:
	@echo "Extracting data from API"
	pipenv run python ./extract/deep_funding_api.py

export_csv:
	@echo "Exporting dfr4_voting_results table to csv"
	$(DBT_COMMAND_PREFIX) run-operation export_csv --args '{"table_name": "dfr4_voting_results"}' --target $(DBT_TARGET)
	@echo "🎉 successfully exported to ${PWD}/exports/dfr4_voting_results.csv"

check:
	@echo "Checking if .csv files are present in $(DATA_DIR)/input"
	@if [ -z "$(wildcard $(DATA_DIR)/input/*.csv)" ]; then \
		echo "⛔️ No .csv files found in $(PWD)/$(DATA_DIR)/input"; \
		echo "💡 Make sure to place the voting_portal data in that folder"; \
		exit 1; \
	fi

# help message
help:
	@echo "Available tasks:"
	@echo "  setup		- Setup project and install dependencies"
	@echo "  generate	- Extract, load, transform data and generate csv output"
	@echo "  ui 		- Generate reports using evidence.dev"
	@echo ""
	@echo ""
	@echo "  development commands:"
	@echo "  export_csv	- Export dfr4_voting_results table to csv"
	@echo "  extract	- Extract data from API"
	@echo "  reports	- Generate reports using evidence"
	@echo "  clean		- Clean dbt and db"
	@echo "  compile	- Run dbt compile"
	@echo "  build		- Run dbt transform performing all the transformations"
	@echo "  debug		- Run dbt debug"
	@echo "  docs		- Build and serve dbt docs"
	@echo "  db	        - Start duckdb on the database"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
