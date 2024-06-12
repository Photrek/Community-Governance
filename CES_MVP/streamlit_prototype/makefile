# phony targets
.PHONY: start

# targets
start:
	@echo "Start Streamlit server"
	@pipenv run streamlit run app.py

dockerize:
	@echo "Dockerize Streamlit app"
	@docker build -t streamlit-app .
	@docker run -p 8501:8501 streamlit-app

# help message
help:
	@echo "Available tasks:"
	@echo "  start		- Start streamlit server"
	@echo "  dockerize	- Dockerize & start Streamlit app"

# By default, when `make` is called without arguments, display help
.DEFAULT_GOAL := help
