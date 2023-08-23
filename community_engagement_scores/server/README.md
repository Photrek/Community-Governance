# Web server for CES

This folder contains configuration files for serving a [Django](https://www.djangoproject.com) web application with a [gunicorn](https://gunicorn.org) server behind a [NGINX](https://www.nginx.com) reverse proxy inside a [Docker](https://www.docker.com) container.


## Installation

1. Install Docker: [Install Docker Engine](https://docs.docker.com/engine/install)
2. Build the Docker container image: `docker build -t ces ..`
    - The package, web app dependencies, server and reverse proxy will be installed automatically inside the container image. This may take a few minutes.


## Usage

### Run the Docker container locally

1. `docker run -dp 127.0.0.1:8000:8080 ces`
2. Wait a few seconds. Then open `http://127.0.0.1:8000/` in a web browser like Chrome or Firefox. If you still get a "The connection was reset" message, reload the site after a few seconds.
3. To stop the server, look for the container id with `docker container list` and use `docker stop <container-id>`.

### Deploy the Docker container on a web hosting service

Please follow the specific guidelines of the web hosting service of your choice, e.g. [DigitalOcean](https://docs.digitalocean.com/products/app-platform/how-to/deploy-from-container-images/), [AWS](https://aws.amazon.com/getting-started/hands-on/deploy-docker-containers/), [GCP](https://cloud.google.com/compute/docs/containers) or many other providers.
