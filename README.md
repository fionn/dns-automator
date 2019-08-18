# Managed DNS

A system to ease the management of DNS A records for an arbitrary number of servers.

## Run

### Locally

Clone, set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

The application expects AWS API secrets as the environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

Other environment variables required are a pseudo-random `SECRET_KEY` for Flask and a `HOSTED_ZONE_DOMAIN`, an FQDN used to identify the zone to be modified.

Run with `./run.py` or `flask run` to serve the web interface in development mode on `localhost:5000` with Flask. To serve with `gunicorn` on `localhost:8000`, run the command in the `Procfile`.

Some toy data is created by `app.server_admin.create_infrastructure`.

### Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/fionn/dns-automator)

`git push heroku`

## Infrastructure

The application requires a Route 53 hosted zone. Provisioning this is automated by Terraform, requiring only the `TF_VAR_hosted_zone_domain` environment variable be set.

Note that the default permissions for the application should not include `route53:CreateHostedZone`, so ensure the correct user keys are sourced. Deployment can be automated end-to-end with `./infrastructure/deploy.sh`, which will push the relevant environment variables to Heroku.
