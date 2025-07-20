import paramiko
import os
from typing import Dict

# Server configurations
servers = {
    "server1": {
        "hostname": "plannedintent.com",
        "username": "root",
        "auth_type": "key",
        "key_filename": "/app/.ssh/vps_manager_key"
    },
    "server2": {
        "hostname": "66.179.208.72",
        "username": "root",
        "auth_type": "password",
        "password": "CODEJOURNEY_PASSWORD"
    },
    "server3": {
        "hostname": "declaresuccess.com",
        "username": "root",
        "auth_type": "password",
        "password": "DECLARESUCCESS_PASSWORD"
    }
}

def connect_to_ssh(server_name):
    """Connects to an SSH server and returns the SSHClient object."""
    if server_name not in servers:
        raise ValueError("Invalid server name")  # Raise ValueError for internal errors
    
    server = servers[server_name]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if server["auth_type"] == "key":
            ssh_client.connect(
                hostname=server["hostname"],
                username=server["username"],
                key_filename=server["key_filename"],
            )
        elif server["auth_type"] == "password":
            env_password = os.getenv(server["password"])
            if env_password is None:
                raise paramiko.AuthenticationException(
                    f"Environment variable '{server['password']}' not set"
                )
            ssh_client.connect(
                hostname=server["hostname"],
                username=server["username"],
                password=env_password,
            )
        else:
            raise ValueError("Invalid authentication type")
        return ssh_client
    except paramiko.AuthenticationException:
        raise  # Re-raise the exception to be handled in the endpoint function
    except paramiko.SSHException as error:
        raise  # Re-raise the exception to be handled in the endpoint function


class SSHSessionManager:
    def __init__(self):
        self.sessions: Dict[str, paramiko.SSHClient] = {}

    def get_session(self, server_name: str) -> paramiko.SSHClient:
        if server_name not in self.sessions:
            self.sessions[server_name] = connect_to_ssh(server_name)
        return self.sessions[server_name]

    def close_session(self, server_name: str):
        if server_name in self.sessions:
            self.sessions[server_name].close()
            del self.sessions[server_name]

    def close_all_sessions(self):
        for server_name in list(self.sessions.keys()):
            self.close_session(server_name)
    
    def get_open_sessions(self) -> list:
        return list(self.sessions.keys())
