"""Blueprint for views"""

import flask
import werkzeug

from .server_admin import dns

BP = flask.Blueprint("views", __name__, url_prefix="/")
APP = flask.current_app

INFRASTRUCTURE = dns.create_infrastructure()
ZONE = dns.Zone()

@APP.route("/")
@APP.route("/index")
def index() -> flask.signals.template_rendered:
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
def servers_ui() -> flask.signals.template_rendered:
    """Renders the server UI"""
    servers = INFRASTRUCTURE.servers
    dns.update_servers(ZONE.records, servers)
    return flask.render_template("servers.html", title="Servers", servers=servers)

@APP.route("/dns")
def dns_ui() -> flask.signals.template_rendered:
    """Renders the DNS UI"""
    return flask.render_template("dns.html", title="DNS", zone_name=ZONE.zone.name,
                                 servers=INFRASTRUCTURE.servers,
                                 dns_records=ZONE.records)

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
                                + "." + ZONE.zone.name)
                    APP.logger.info("add %s", server.name)
                    ZONE.add_server(server)
                elif action == "remove":
                    flask.flash("Removed server " + server.name + \
                                " from DNS A record "
                                +  dns.CLUSTER_MAP[server.cluster_id].subdomain
                                + "." + ZONE.zone.name)
                    APP.logger.info("remove %s", server.name)
                    ZONE.remove_server(server)
                break

    return flask.redirect("/servers")
