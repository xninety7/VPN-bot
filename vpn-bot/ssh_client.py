import paramiko
import os

def ssh_run(host, command):
    key_path = os.getenv("SSH_KEY_PATH", "/root/.ssh/v2ray_monitor")
    user = os.getenv("PH_USER", "root")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            username=user,
            key_filename=key_path,
            timeout=30
        )
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write("y\n")
        stdin.flush()
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err
    finally:
        client.close()
