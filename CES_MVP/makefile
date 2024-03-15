# Define tasks
.PHONY: db
db:
	@echo "Spawning DuckDB using init.sql"
	duckdb --init init.sql

.PHONY: report
report:
	@echo "Generates a report.xlsx from the given input data"
	duckdb --init init.sql < report.sql

# Define a default target to display all possible tasks
.PHONY: help
help:
	@echo "Available tasks:"
	@echo "  db 	- Spawning a in memory duckDB loading all .csv files as tables"
	@echo "  report - Generates a report.xlsx from the given input data"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
