#!/usr/bin/env python3
"""DNS logic"""

import os
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import NamedTuple, Optional

import boto3

NameDomain = NamedTuple("NameDomain", [("name", str), ("subdomain", str)])
Infrastructure = NamedTuple("Infrastructure", [("clusters", list["Cluster"]),
                                               ("servers", list["Server"])])

CLUSTER_MAP = {1: NameDomain("Los Angeles", "la"),
               2: NameDomain("New York", "nyc"),
               3: NameDomain("Frankfurt", "fra"),
               4: NameDomain("Hong Kong", "hk"),
               5: NameDomain("Tokyo", "tyo"),
               6: NameDomain("Dublin", "dub")}

SUBDOMAIN_MAP = {"la": "Los Angeles",
                 "nyc": "New York",
                 "fra": "Frankfurt",
                 "hk": "Hong Kong",
                 "tyo": "Tokyo",
                 "dub": "Dublin",
                 "sg": "Singapore"}

# pylint: disable=too-few-public-methods
@dataclass
class Server:
    """Server model"""
    server_id: int
    cluster_id: int
    id_in_cluster: int
    ip_address: IPv4Address
    dns: Optional[str] = None

    @property
    def name(self) -> str:
        """Server name"""
        return "-".join([CLUSTER_MAP[self.cluster_id].subdomain,
                         str(self.id_in_cluster)])
    @property
    def cluster_name(self) -> str:
        """Cluster name"""
        return CLUSTER_MAP[self.cluster_id].name

    def __str__(self) -> str:
        return self.name

# pylint: disable=too-few-public-methods
class Cluster:
    """A class for cluster objects"""

    def __init__(self, cluster_id: int, subdomain: str) -> None:
        self.cluster_id = cluster_id
        self.subdomain = subdomain
        self.server_instances: list[Server] = []

    @property
    def cluster_name(self) -> str:
        """Returns the friendly name"""
        return SUBDOMAIN_MAP[self.subdomain]

    def __repr__(self) -> str:
        return f"<{type(self).__name__}(cluster_id={self.cluster_id})>"

    # pylint: disable=invalid-name
    def create_server(self, server_id: int, ip: IPv4Address) -> Server:
        """Factory method for server creation"""
        server = Server(server_id=server_id, cluster_id=self.cluster_id,
                        id_in_cluster=len(self.server_instances) + 1,
                        ip_address=ip)
        self.server_instances.append(server)
        return server

class Zone:
    """Zone container"""

    def __init__(self, hosted_zone_domain: str) -> None:
        self.r53 = boto3.client("route53")
        self.name = hosted_zone_domain
        hosted_zone = self._get_hosted_zone()
        self.id = hosted_zone["Id"].split("/")[-1] # pylint: disable=invalid-name

    def _get_hosted_zone(self) -> dict:
        for zone in self.r53.list_hosted_zones()["HostedZones"]:
            if zone["Name"] == self.name:
                return zone
        raise RuntimeError(f"Failed to find hosted zone for {self.name}")

    @property
    def records(self) -> list[dict]:
        """Flexible record property"""
        record_sets = self.r53 \
                      .list_resource_record_sets(HostedZoneId=self.id) \
                      ["ResourceRecordSets"]
        return [r for r in record_sets \
                if (r["Type"] == "A" and r["Name"] != self.name)]

    @staticmethod
    def ips_from_record(record: dict) -> set[IPv4Address]:
        """Helper to get IP addresses from a given record"""
        ips = set()
        for value in record["ResourceRecords"]:
            ips.add(IPv4Address(value["Value"]))
        return ips

    def _a_record(self, name: str, ips: set[IPv4Address],
                  action: str, ttl: int = 30) -> None:
        change_batch = {
            "Comment": "add f{} -> {}"  # pylint: disable=consider-using-f-string
                       .format(name, ", ".join([ip.exploded for ip in ips])),
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": name,
                        "Type": "A",
                        "TTL": ttl,
                        "ResourceRecords": [{"Value": ip.exploded}
                                            for ip in ips]
                    }
                }
            ]
        }

        self.r53.change_resource_record_sets(HostedZoneId=self.id,
                                             ChangeBatch=change_batch)

    def add_server(self, server: Server) -> None:
        """Adds the server's IP to the cluster's subdomain."""
        fqdn = CLUSTER_MAP[server.cluster_id].subdomain + "." + self.name

        ips: set[IPv4Address] = set()
        for record in self.records:
            if fqdn == record["Name"]:
                ips = self.ips_from_record(record)
                break

        ips.add(server.ip_address)

        self._a_record(fqdn, ips, "UPSERT")
        server.dns = fqdn

    def remove_server(self, server: Server) -> None:
        """Removes the server's IP from the DNS record."""
        fqdn = CLUSTER_MAP[server.cluster_id].subdomain + "." + self.name

        ips: set[IPv4Address] = set()
        for record in self.records:
            if fqdn == record["Name"]:
                ips = self.ips_from_record(record)
                break

        if server.ip_address not in ips:
            return

        ips = set(filter(lambda x: x != server.ip_address, ips))

        if ips:
            self._a_record(fqdn, ips, "UPSERT")
        else:
            ips.add(server.ip_address)
            self._a_record(fqdn, ips, "DELETE")

        server.dns = None

def create_infrastructure() -> Infrastructure:
    """Instantiates clusters and their servers"""
    clusters = []
    for cluster_id, ident in CLUSTER_MAP.items():
        clusters.append(Cluster(cluster_id, ident.subdomain))

    clusters[0].create_server(1, ip=IPv4Address("2.4.6.8"))
    clusters[1].create_server(2, ip=IPv4Address("1.0.1.1"))
    clusters[2].create_server(3, ip=IPv4Address("5.6.7.8"))
    clusters[3].create_server(4, ip=IPv4Address("4.3.2.1"))
    clusters[3].create_server(5, ip=IPv4Address("1.2.3.4"))
    clusters[3].create_server(6, ip=IPv4Address("1.2.3.5"))
    clusters[3].create_server(7, ip=IPv4Address("1.2.3.6"))
    clusters[4].create_server(8, ip=IPv4Address("8.1.1.1"))
    clusters[5].create_server(9, ip=IPv4Address("9.1.1.1"))

    servers = []
    for cluster in clusters:
        for server in cluster.server_instances:
            servers.append(server)

    servers.sort(key=lambda x: x.name)

    return Infrastructure(clusters, servers)

def print_servers(server_instances: list[Server]) -> None:
    """ASCII analogy of the server UI"""
    print("\n\033[1mID\t Name\t Cluster\t IP\t\t DNS\033[0m")
    for server in server_instances:
        print(server.server_id, "\t", server.name, "\t",
              CLUSTER_MAP[server.cluster_id].name, "\t",
              server.ip_address, server.dns)

def print_dns(dns_records: list[dict], server_instances: list[Server]) -> None:
    """ASCII analogy of the DNS UI"""
    print("\n\033[1mDomain\t\t\t\t\t IP(s)\t\t Server(s)\t Cluster\033[0m")
    for record in dns_records:
        matching_servers = []
        for server in server_instances:
            if server.ip_address in Zone.ips_from_record(record):
                matching_servers.append(server)
        print(record["Name"], "\t", Zone.ips_from_record(record), "\t",
              [server.name for server in matching_servers], "\t",
              [CLUSTER_MAP[server.cluster_id].name
               for server in matching_servers])

def update_servers(records: list[dict], servers: list[Server]) -> None:
    """Assigns to each server instance their DNS record name"""
    for server in servers:
        server.dns = None
        for record in records:
            if server.ip_address in Zone.ips_from_record(record):
                server.dns = record["Name"]

def main() -> None:
    """Entry point"""
    zone = Zone(os.environ["HOSTED_ZONE_DOMAIN"])
    infrastructure = create_infrastructure()
    update_servers(zone.records, infrastructure.servers)

    print_servers(infrastructure.servers)
    print_dns(zone.records, infrastructure.servers)

if __name__ == "__main__":
    main()
