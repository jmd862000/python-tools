#!/usr/bin/env python3
# iptools.py
import ipaddress
import sys
import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="Function to perform",dest="expand")
parser_expand = subparsers.add_parser("expand",help="Expand a range of host addresses")
parser_expand.add_argument("--network", help = "CIDR Address to expand", metavar="NET",required=True)
parser_expand.add_argument("--version", help = "IP Version (e.g. 4 or 6)", metavar="VER", default=4, choices=['4','6'])

def list_addresses(ip:str(),version:int()) -> list():	
    result = []
    if version == 4:
        i = ipaddress.IPv4Interface(ip)
        if i.network.num_addresses>65536:
            start = i.network.network_address+1
            end = i.network.broadcast_address-1
            return [start.exploded,end.exploded]
    elif version == 6:
        i = ipaddress.IPv6Interface(ip)
        start = i.network.network_address+1
        end = i.network.broadcast_address-1
        return [start.exploded,end.exploded]
    else:
        raise ipaddress.AddressValueError("Invalid IP Version")
    result = [sIP.exploded for sIP in i.network.hosts()]
    return result	

options = parser.parse_args()

if options.network and options.expand:
    for ip in list_addresses(options.network,int(options.version)):
        print(ip)
else:
    parser.print_help()
