#!/bin/bash
set -e
iptables -P INPUT ACCEPT
# WARNING: Unrecognized firewall rule format skipped: target     prot opt source               destination
iptables -P FORWARD ACCEPT
# WARNING: Unrecognized firewall rule format skipped: target     prot opt source               destination
iptables -P OUTPUT ACCEPT
# WARNING: Unrecognized firewall rule format skipped: target     prot opt source               destination
exec "$@"