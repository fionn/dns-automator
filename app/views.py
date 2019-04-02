"""flask views object"""

import flask
import werkzeug
from app import app
from .dns.dns import Cluster, Server, dns, update_server_dns, create_instances

app.secret_key = "lQq8UJPnzpqWpKAIE0PrC0tddlWGXXuBVHwbtks65j0="

@app.route("/")
@app.route("/index")
def index() -> flask.signals.template_rendered:
    """index"""
    links = [
        {
            'title': 'Currently published DNS entries',
            'url': 'dns'
        },
        {
            'title': 'Servers',
            'url': 'servers'
        }
    ]
    return flask.render_template("index.html", title="Home", links=links)

@app.route("/servers")
def servers_ui() -> flask.signals.template_rendered:
    """renders the server UI"""
    update_server_dns(dns())
    servers = Server.instances
    return flask.render_template("servers.html", title="Servers", servers=servers)

@app.route("/dns")
def dns_ui() -> flask.signals.template_rendered:
    """renders the DNS UI"""
    return flask.render_template("dns.html", title="DNS", zone=Cluster.zone,
                                 servers=Server.instances, dns_records=dns())

@app.route("/rotate", methods=["GET", "POST"])
def rotate() -> werkzeug.wrappers.Response:
    """ Moves the server(s) into / out of DNS rotation """
    if flask.request.method == "POST":
        action = flask.request.form.get("action")
        server_id = int(flask.request.form.get("server")) # type: ignore

        for server in Server.instances:
            if server.server_id == server_id:
                if action == "add":
                    flask.flash("Added server " + server.friendly_name + \
                                " to DNS A record " + server.subdomain + \
                                "." + server.zone.name)
                    print("add", server.friendly_name)
                    server.add_to_rotation()
                elif action == "remove":
                    flask.flash("Removed server " + server.friendly_name + \
                                " from DNS A record " + server.subdomain + \
                                "." + server.zone.name)
                    print("remove", server.friendly_name)
                    server.remove_from_rotation()
                break

    return flask.redirect("/servers")

def main() -> None:
    """main view function"""
    create_instances()
    records = dns()
    update_server_dns(records)
    #print_servers()
    #print_dns(records)

main()
