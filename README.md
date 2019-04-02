# Automatically Managed DNS

A system to automate the management of DNS A records for a large number of servers.

## Run

### Locally

Clone, set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

Make a `credentials.py` file in `/app/dns/`. This should contain the API secrets as the constants `ACCESS_ID`, `ACCESS_SECRET`.

Then run with `./run.py` to serve the web interface on `localhost:5000`. In `dns.create_instances()` some toy data is created.

Currently deployed to [`lit-tundra-97584.herokuapp.com/`](https://lit-tundra-97584.herokuapp.com/).

