#!/usr/bin/env python3
"""DNS logic"""

import os
from typing import List

import boto
import route53

AWS_ACCESS_ID = os.environ["AWS_ACCESS_ID"]
AWS_ACCESS_SECRET = os.environ["AWS_ACCESS_SECRET"]

# pylint: disable=too-few-public-methods
class Cluster():
    """A class for cluster objects"""
    instances: List["Cluster"] = []
    records: List["route53.resource_record_set.AResourceRecordSet"] = []
    zone: "route53.hosted_zone.HostedZone" = None
    n = 4 # Number of unique clusters

    def __init__(self, cluster_id: int) -> None:
        self.instances.append(self)
        self.cluster_id = cluster_id
        self.cluster_name = self._name()
        self.subdomain = self._subdomain()

    def __repr__(self) -> str:
        return f"<{type(self).__name__}(cluster_id={self.cluster_id})>"

    def _name(self) -> str:
        name_dict = {1: "Los Angeles",
                     2: "New York",
                     3: "Frankfurt",
                     4: "Hong Kong"}
        return name_dict[self.cluster_id]

    def _subdomain(self) -> str:
        subdomain_dict = {"Los Angeles": "la",
                          "New York": "nyc",
                          "Frankfurt": "fra",
                          "Hong Kong": "hk"}
        return subdomain_dict[self.cluster_name]

    def create_server(self, server_name: str) -> "Server":
        """Factory method for server creation"""
        return Server(self.cluster_id, server_name)

class Server(Cluster):
    """Cluster child class"""
    instances: list = []

    def __init__(self, cluster_id: int, friendly_name: str) -> None:
        super().__init__(cluster_id)
        self.server_id = len(self.instances)
        self.friendly_name = friendly_name
        self.ip_string = "0.0.0.0"
        self.dns = "NONE"

    def add_to_rotation(self) -> None:
        """Adds the server's IP to the cluster's subdomain."""
        fqdn = self.subdomain + "." + self.zone.name

        # If records could simply be added & removed, this would make the
        # UI behave better with synchronous post requests.
        # Instead we have to rewrite the whole record.

        ips: list = []
        for record in self.records:
            if fqdn == record.name:
                ips = record.records[:]
                break

        ips.append(self.ip_string)

        conn = boto.connect_route53(aws_access_key_id=AWS_ACCESS_ID,
                                    aws_secret_access_key=AWS_ACCESS_SECRET)

        changes = boto.route53.record.ResourceRecordSets(conn, self.zone.id)
        change = changes.add_change("UPSERT", fqdn, "A")

        for ip_address in set(ips):
            change.add_value(ip_address)

        changes.commit()

    def remove_from_rotation(self) -> None:
        """Removes the server's IP from the DNS record."""
        fqdn = self.subdomain + "." + self.zone.name

        ips: list = []
        for record in self.records:
            if fqdn == record.name:
                ips = record.records[:]
                break

        if self.ip_string not in ips:
            return

        ips = list(filter(lambda x: x != self.ip_string, ips))

        conn = boto.connect_route53(aws_access_key_id=AWS_ACCESS_ID,
                                    aws_secret_access_key=AWS_ACCESS_SECRET)

        changes = boto.route53.record.ResourceRecordSets(conn, self.zone.id)

        # This should be simple, but seemingly the API complains unless
        # it's updated in this arduous fashion.

        if ips:
            change = changes.add_change("UPSERT", fqdn, "A")
            for ip_address in set(ips):
                change.add_value(ip_address)
        else:
            change = changes.add_change("DELETE", fqdn, "A")
            change.add_value(self.ip_string)

        changes.commit()

def assign_dns() -> list:
    """Grabs all A records for the hosted zone
    and assigns them to class variables"""
    print("Fetching DNS A records... ", end="", flush=True)

    conn = route53.connect(aws_access_key_id=AWS_ACCESS_ID,
                           aws_secret_access_key=AWS_ACCESS_SECRET)

    zone = list(conn.list_hosted_zones())[0]
    records = [record for record in zone.record_sets]

    records = [r for r in zone.record_sets \
               if (r.rrset_type == "A" and r.name != zone.name)]

    Cluster.zone = zone
    Cluster.records = records

    print("done")

    return records

def create_instances() -> None:
    """Instantiates clusters and their servers"""
    clusters = []
    for i in range(1, Cluster.n + 1):
        clusters.append(Cluster(i))

    la1 = clusters[0].create_server("la1")
    ny1 = clusters[1].create_server("ny1")
    fr1 = clusters[2].create_server("fr1")
    hk1 = clusters[3].create_server("hk1")
    hk2 = clusters[3].create_server("hk2")

    la1.ip_string = "2.4.6.8"
    ny1.ip_string = "1.1.1.1"
    fr1.ip_string = "5.6.7.8"
    hk1.ip_string = "4.3.2.1"
    hk2.ip_string = "1.2.3.4"

    Server.instances.sort(key=lambda x: x.friendly_name)

def update_server_dns(dns_records: list) -> None:
    """Assigns to each server instance their DNS record name"""
    for server in Server.instances:
        server.dns = "NONE"
        for record in dns_records:
            if server.ip_string in record.records:
                server.dns = record.name

def print_servers() -> None:
    """ASCII analogy of the server UI"""
    print("\n\033[1mID\t Name\t Cluster\t DNS\t\t\t IP\033[0m")
    for server in Server.instances:
        print(server.server_id, "\t", server.friendly_name, "\t",
              server.cluster_name, "\t", server.dns, "\t", server.ip_string)

def print_dns(dns_records: list) -> None:
    """ASCII analogy of the DNS UI"""
    print("\n\033[1mDomain\t\t\t\t\t IP(s)\t\t Server(s)\t Cluster\033[0m")
    for record in dns_records:
        matching_servers = []
        for server in Server.instances:
            if server.ip_string in record.records:
                matching_servers.append(server)
        print(record.name, "\t", record.records, "\t",
              [server.friendly_name for server in matching_servers], "\t",
              [server.cluster_name for server in matching_servers])

def main() -> None:
    """Entry point"""
    create_instances()
    records = assign_dns()
    update_server_dns(records)

    print_servers()
    print_dns(records)

if __name__ == "__main__":
    main()
