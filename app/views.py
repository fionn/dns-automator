from flask import render_template, request, redirect, flash
from app import app
from .dns.dns import *

app.secret_key = 'lQq8UJPnzpqWpKAIE0PrC0tddlWGXXuBVHwbtks65j0='

@app.route('/')
@app.route('/index')
def index():
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
    return render_template("index.html", title = 'Home', links = links)

@app.route('/servers')
def servers_ui():
    update_server_dns(dns())
    servers = Server.instances
    return render_template("servers.html", title = "Servers", servers = servers)

@app.route('/dns')
def dns_ui():
    return render_template("dns.html", title = "DNS", zone = Cluster.zone, 
                            servers = Server.instances, dns_records = dns())

@app.route('/rotate', methods = ['GET', 'POST'])
def rotate():
    """ Moves the server(s) into / out of DNS rotation """
    if request.method == 'POST':
        action = request.form.get("action")
        server_id = int(request.form.get("server"))

        for server in Server.instances:
            if server.server_id == server_id:
                if action == "add":
                    flash("Added server " + server.friendly_name + \
                          " to DNS A record " + server.subdomain + \
                          "." + server.zone.name)
                    print("add", server.friendly_name)
                    server.add_to_rotation()
                elif action == "remove":
                    flash("Removed server " + server.friendly_name + \
                          " from DNS A record " + server.subdomain + \
                          "." + server.zone.name)
                    print("remove", server.friendly_name)
                    server.remove_from_rotation()
                break

    return redirect('/servers')

create_instances()
dns_records = dns()
update_server_dns(dns_records)

#print_servers()
#print_dns(dns_records)

