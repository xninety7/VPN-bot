import os
import time
import socket
import re
from dotenv import load_dotenv
load_dotenv()

from ssh_client import ssh_run
from namecom import create_dns_record

PH_HOST = os.getenv("PH_HOST")
HK_HOST = os.getenv("HK_HOST")
SG_HOST = os.getenv("SG_HOST")


def get_host(server):
    hosts = {
        "ph": PH_HOST,
        "hk": HK_HOST,
        "sg": SG_HOST,
    }
    return hosts.get(server)

def wait_for_dns(domain, expected_ip, timeout=300, interval=15):
    print(f"Waiting for {domain} to resolve to {expected_ip}...")
    elapsed = 0
    while elapsed < timeout:
        try:
            resolved = socket.gethostbyname(domain)
            print(f"DNS resolved: {domain} -> {resolved}")
            if resolved == expected_ip:
                return True
        except socket.gaierror:
            print(f"DNS not yet resolved, retrying in {interval}s...")
        time.sleep(interval)
        elapsed += interval
    return False

def execute_tool(name, args):
    if name == "create_v2ray_user":
        return create_v2ray_user(args)
    if name == "delete_v2ray_user":
        return delete_v2ray_user(args)
    if name == "restart_service":
        return restart_service(args)
    if name == "get_logs":
        return get_logs(args)
    if name == "list_users":
        return list_users(args)
    return "Unknown tool"

def create_v2ray_user(args):
    username = args["username"].lower()
    server = args["server"]
    subdomain = username
    domain = f"{subdomain}.neweb.me"
    output = ssh_run(host, f"v2ray add ws {domain}", srv)

    servers = []
    if server == "both":
        servers = [("ph", PH_HOST), ("hk", HK_HOST), ("sg", SG_HOST)]
    else:
        servers = [(server, get_host(server))]

    results = []
    for srv, host in servers:
        try:
            # Step 1: Create DNS record
            print(f"Creating DNS record {domain} -> {host}")
            create_dns_record(subdomain, host)

            # Step 2: Wait for DNS propagation
            resolved = wait_for_dns(domain, host)
            if not resolved:
                results.append(f"**Server:** {srv.upper()}\n**Status:** DNS did not propagate in time")
                continue

            # Step 3: Run v2ray add on server
            print(f"Running v2ray add on {srv}")
            output = ssh_run(host, f"v2ray add ws {domain}", srv)
            print(f"v2ray output: {output}")

            # Step 4: Strip ANSI color codes then extract VMess URL
            clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
            vmess_url = ""
            for line in clean_output.splitlines():
                line = line.strip()
                if line.startswith("vmess://") or line.startswith("vless://"):
                    vmess_url = line
                    break

            url_line = f"\n**URL:** `{vmess_url}`" if vmess_url else "\n**URL:** Not found"
            results.append(f"**Server:** {srv.upper()}\n**Domain:** {domain}\n**Protocol:** VMess-WS-TLS\n**Status:** Created successfully{url_line}")

        except Exception as e:
            results.append(f"**Server:** {srv.upper()}\n**Status:** Error - {str(e)}")

    return "\n\n".join(results)

def restart_service(args):
    server = args["server"]
    service = args["service"]
    host = get_host(server)
    try:
        output = ssh_run(host, f"systemctl restart {service}", server)
        status = ssh_run(host, f"systemctl is-active {service}", server)
        return f"**Server:** {server.upper()}\n**Service:** {service}\n**Status:** {status.strip()}"
    except Exception as e:
        return f"**Server:** {server.upper()}\n**Status:** Error - {str(e)}"

def get_logs(args):
    server = args["server"]
    service = args["service"]
    lines = args.get("lines", 50)
    host = get_host(server)
    try:
        output = ssh_run(host, f"journalctl -u {service} -n {lines} --no-pager", server)
        return f"**Logs:** {service} on {server.upper()}\n```\n{output}\n```"
    except Exception as e:
        return f"**Status:** Error - {str(e)}"

def delete_v2ray_user(args):
    username = args["username"].lower()
    server = args["server"]
    if username.endswith(".neweb.me"):
        domain = username
    else:
        domain = f"{username}.neweb.me"
    host = get_host(server)
    try:
        output = ssh_run(host, f"v2ray delete ws {domain} 2>&1 || v2ray remove ws {domain} 2>&1 || v2ray del ws {domain} 2>&1", server)
        return f"**Server:** {server.upper()}\n**Domain:** {domain}\n**Status:** Deleted successfully\n**Output:**\n```\n{output}\n```"
    except Exception as e:
        return f"**Server:** {server.upper()}\n**Domain:** {domain}\n**Status:** Error - {str(e)}"

def list_users(args):
    server = args["server"]
    host = get_host(server)
    try:
        output = ssh_run(host, "ls /etc/v2ray/conf/ | grep VMess-WS-TLS")
        return f"**Users on {server.upper()}:**\n{output}"
    except Exception as e:
        return f"**Status:** Error - {str(e)}"
