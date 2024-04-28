# phony targets
.PHONY: start

# targets
start:
	@echo "Start Streamlit server"
	@pipenv run streamlit run app.py

# help message
help:
	@echo "Available tasks:"
	@echo "  start		- Start streamlit server"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
