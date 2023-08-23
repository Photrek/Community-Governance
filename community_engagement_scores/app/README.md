# Web application for CES

This folder contains a web application based on the popular web framework [Django](https://www.djangoproject.com).

## Installation

1. Install the package for CES: See [pkg](../pkg)
2. Install the dependencies of the web app: `pip install -r requirements.txt`

## Usage

### Run the app locally with a testserver

1. `python manage.py migrate`
2. `DEBUG=True python manage.py runserver`
3. Open `http://127.0.0.1:8000/` in a web browser like Chrome or Firefox

### Deploy the app in a production environment

See [server](../server)


## Development notes

This Django app follows the default project structure explained in [introductory tutorials](https://docs.djangoproject.com/en/4.2/intro/tutorial01/) and created by `django-admin startproject <name>`. The most relevant folders and files are:

- [ces_project](ces_project): Django project
  - [settings.py](ces_project/settings.py): Main settings of the project.
- [swae_portal](swae_portal): Django app
  - [urls.py](swae_portal/urls.py): Definition of the HTTP entry points.
  - [views.py](swae_portal/views.py): Definition of the views and forms that make up the GUI.
  - [analysis_workflow.py](swae_portal/analysis_workflow.py): A custom module that implements state management for the step-by-step workflow provided to the user in the app.
