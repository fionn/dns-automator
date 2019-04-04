# Automatically Managed DNS

A system to automate the management of DNS A records for an arbitrary number of servers.

## Run

### Locally

Clone, set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

The application expects AWS API secrets as the environment variables `AWS_ACCESS_ID`, `AWS_ACCESS_SECRET` and a pseudo-random `SECRET_KEY`.

Run with `./run.py` or `flask run` to serve the web interface in development mode on `localhost:5000` with Flask. To serve with `gunicorn` on `localhost:8000`, run the command in `Procfile`. Simulate a deployment with `heroku local`.

Some toy data is created by `dns.create_instances`.

### Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/fionn/dns-automator)
