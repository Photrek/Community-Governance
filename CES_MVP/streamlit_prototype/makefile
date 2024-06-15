# phony targets
.PHONY: start

# targets
start_local:
	@echo "Start Streamlit server"
	@pipenv run streamlit run app.py

dockerize:
	@echo "Dockerize Streamlit app"
	@echo "Fetch latest version"
	@git pull
	@docker build -t streamlit-app .
	@docker run -p 8501:8501 streamlit-app

# help message
help:
	@echo "Available tasks:"
	@echo "  start_local	- Start streamlit server"
	@echo "  dockerize		- Dockerize & start Streamlit app"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
