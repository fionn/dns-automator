# Managed DNS

A system to ease the management of DNS A records for an arbitrary number of servers.

## Run

### Locally

Clone, set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

The application expects AWS API secrets as the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and a pseudo-random `SECRET_KEY` for Flask.

Run with `./run.py` or `flask run` to serve the web interface in development mode on `localhost:5000` with Flask. To serve with `gunicorn` on `localhost:8000`, run the command in the `Procfile`.

Some toy data is created by `app.server_admin.create_infrastructure`.

### Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/fionn/dns-automator)
