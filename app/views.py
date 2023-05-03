"""Blueprint for views"""

import os

import flask
import werkzeug

from .server_admin import dns

HOSTED_ZONE_DOMAIN = os.environ["HOSTED_ZONE_DOMAIN"]

BP = flask.Blueprint("views", __name__, url_prefix="/")
APP = flask.current_app

INFRASTRUCTURE = dns.create_infrastructure()
ZONE = dns.Zone(HOSTED_ZONE_DOMAIN)

@APP.route("/")
@APP.route("/index")
def index() -> str:
    """index"""
    links = [
        {
            "title": "Currently published DNS entries",
            "url": "dns"
        },
        {
            "title": "Servers",
            "url": "servers"
        }
    ]
    return flask.render_template("index.html", title="Home", links=links)

@APP.route("/servers")
def servers_ui() -> str:
    """Renders the server UI"""
    servers = INFRASTRUCTURE.servers
    dns.update_servers(ZONE.records, servers)
    return flask.render_template("servers.html", title="Servers", servers=servers)

@APP.route("/dns")
def dns_ui() -> str:
    """Renders the DNS UI"""
    return flask.render_template("dns.html", title="DNS", zone_name=ZONE.name,
                                 servers=INFRASTRUCTURE.servers,
                                 dns_records=ZONE.records,
                                 ips_from_record=ZONE.ips_from_record)

@APP.route("/rotate", methods=["GET", "POST"])
def rotate() -> werkzeug.wrappers.Response:
    """Moves the server(s) into / out of DNS rotation"""
    if flask.request.method == "POST":
        action = flask.request.form.get("action")
        server_id = int(flask.request.form.get("server")) # type: ignore

        for server in INFRASTRUCTURE.servers:
            if server.server_id == server_id:
                if action == "add":
                    flask.flash("Added server " + server.name + \
                                " to DNS A record "
                                + dns.CLUSTER_MAP[server.cluster_id].subdomain
                                + "." + ZONE.name)
                    APP.logger.info("add %s", server.name)
                    ZONE.add_server(server)
                elif action == "remove":
                    flask.flash("Removed server " + server.name + \
                                " from DNS A record "
                                +  dns.CLUSTER_MAP[server.cluster_id].subdomain
                                + "." + ZONE.name)
                    APP.logger.info("remove %s", server.name)
                    ZONE.remove_server(server)
                break

    return flask.redirect("/servers")
