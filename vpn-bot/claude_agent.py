from tools import execute_tool

HELP_TEXT = """
*VPN Ops Bot Commands*

*V2Ray Users:*
- `add user <name> on <ph|hk|sg|both>` — Create a new V2Ray user
- `list users on <ph|hk|sg>` — List existing users
- `delete user <name> on <ph|hk|sg>` — Delete a user

*Services:*
- `restart v2ray on <ph|hk|sg>` — Restart V2Ray
- `restart caddy on <ph|hk|sg>` — Restart Caddy

*Logs:*
- `logs v2ray on <ph|hk|sg>` — Get V2Ray logs
- `logs caddy on <ph|hk|sg>` — Get Caddy logs
- `logs v2ray on <ph|hk|sg> <number>` — Get last N lines

*Other:*
- `help` — Show this message
"""

def parse_server(text):
    if "all" in text:
        return "all"
    elif " sg" in text or "sg " in text:
        return "sg"
    elif " hk" in text or "hk " in text:
        return "hk"
    elif " ph" in text or "ph " in text:
        return "ph"
    return None

def parse_service(text):
    if "caddy" in text:
        return "caddy"
    elif "v2ray" in text:
        return "v2ray"
    return None

def run_agent(text):
    text = text.lower().strip()

    # help
    if text == "help" or text == "hi" or text == "hello":
        return HELP_TEXT

    # add user <name> on <server>
    if text.startswith("add user"):
        server = parse_server(text)
        if not server:
            return "❌ Please specify a server: `add user <name> on <ph|hk|both>`"
        try:
            # extract username — word after "add user"
            parts = text.replace("add user", "").strip().split()
            username = parts[0]
        except:
            return "❌ Please provide a username: `add user <name> on <ph|hk|both>`"

        return execute_tool("create_v2ray_user", {
            "username": username,
            "server": server
        })

    # list users on <server>
    if "list users" in text or "list user" in text:
        server = parse_server(text)
        if not server or server == "both":
            return "❌ Please specify a server: `list users on <ph|hk>`"
        return execute_tool("list_users", {"server": server})

    # delete user <name> on <server>
    if text.startswith("delete user"):
        server = parse_server(text)
        if not server or server == "both":
            return "❌ Please specify a server: `delete user <name> on <ph|hk>`"
        try:
            parts = text.replace("delete user", "").strip().split()
            username = parts[0]
        except:
            return "❌ Please provide a username: `delete user <name> on <ph|hk>`"
        return execute_tool("delete_v2ray_user", {
            "username": username,
            "server": server
        })

    # restart <service> on <server>
    if text.startswith("restart"):
        server = parse_server(text)
        service = parse_service(text)
        if not server or server == "all":
            return "❌ Please specify a server: `restart <v2ray|caddy> on <ph|hk>`"
        if not service:
            return "❌ Please specify a service: `restart <v2ray|caddy> on <ph|hk>`"
        return execute_tool("restart_service", {
            "server": server,
            "service": service
        })

    # logs <service> on <server> [lines]
    if text.startswith("logs") or "logs" in text:
        server = parse_server(text)
        service = parse_service(text)
        if not server or server == "all":
            return "❌ Please specify a server: `logs <v2ray|caddy> on <ph|hk>`"
        if not service:
            return "❌ Please specify a service: `logs <v2ray|caddy> on <ph|hk>`"

        # extract optional line count
        lines = 50
        parts = text.split()
        for part in parts:
            if part.isdigit():
                lines = int(part)
                break

        return execute_tool("get_logs", {
            "server": server,
            "service": service,
            "lines": lines
        })

    return f"❓ Unknown command: `{text}`\nType `help` to see available commands."
