from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import paramiko
import subprocess
import platform

from session_manager import SSHSessionManager
from app.routers.servers import router as servers_router
from app.database import get_db

load_dotenv()  # Load environment variables from .env file

API_KEY = os.getenv("API_KEY")

app = FastAPI()
session_manager = SSHSessionManager()

# API key authentication
api_key_header = APIKeyHeader(name="Authorization")

import json

# Function to load server configurations from servers.json
def load_server_configs():
    with open("servers.json", "r") as f:
        return json.load(f)

# Function to save server configurations to servers.json
def save_server_configs(configs):
    with open("servers.json", "w") as f:
        json.dump(configs, f, indent=4)

# Load initial server configurations
servers = load_server_configs()


def ping_vps(hostname: str) -> bool:
    """Return True if the host responds to a single ping."""
    # Platform-specific parameters for ping command
    count_param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        subprocess.check_call(
            ["ping", count_param, "1", timeout_param, "1", hostname],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False

def get_api_key(api_key: str = Depends(api_key_header)):
    if API_KEY is None or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="That API key is invalid. Try again.")

@app.get("/")
def read_root():
    return {"message": "Hello, W!"}

class VPSStatus(BaseModel):
    status: str

@app.get("/vps/status", dependencies=[Depends(get_api_key)])
def get_vps_status():
    # Logic to retrieve VPS status
    vps_status = VPSStatus(status="running: Session Manager")
    return vps_status

class CommandRequest(BaseModel):
    command: str

@app.post("/execute/container_bash_command", dependencies=[Depends(get_api_key)])
def execute_command(request: CommandRequest):
    try:
        # Execute the bash command securely
        output = subprocess.check_output(request.command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        #result = subprocess.run(request.command, shell=True, capture_output=True, text=True)
        
        output = output.split('\n')
        return {"output": output}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {e.output}")

def connect_to_ssh(server_name: str, db: Session):
    """Connect to an SSH server using configuration from the database.

    Parameters
    ----------
    server_name: str
        The hostname or identifier of the server.
    db: Session
        Active database session used to retrieve the server configuration.

    Returns
    -------
    paramiko.SSHClient
        Connected SSH client.
    """

    from app.models.server import Server

    server = (
        db.query(Server)
        .filter((Server.hostname == server_name) | (Server.public_ip == server_name))
        .first()
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    tags = server.tags or {}
    username = tags.get("username", "root")
    auth_type = tags.get("auth_type", "key")
    key_filename = tags.get("key_filename")
    password_env = tags.get("password_env")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if auth_type == "key":
            if not key_filename:
                raise HTTPException(status_code=500, detail="Missing SSH key path")
            ssh_client.connect(hostname=server.hostname, username=username, key_filename=key_filename)
        elif auth_type == "password":
            if not password_env:
                raise HTTPException(status_code=500, detail="Missing password environment variable")
            env_password = os.getenv(password_env)
            if env_password is None:
                raise HTTPException(status_code=500, detail=f"Environment variable '{password_env}' not set")
            ssh_client.connect(hostname=server.hostname, username=username, password=env_password)
        else:
            raise ValueError("Invalid authentication type")
        return ssh_client
    except paramiko.AuthenticationException:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except paramiko.SSHException as error:
        raise HTTPException(status_code=500, detail=f"SSH connection error: {str(error)}")

def execute_remote_command(ssh_client: paramiko.SSHClient, command: str) -> list:
    """Execute a command on the remote server and return its output lines.

    Parameters
    ----------
    ssh_client: paramiko.SSHClient
        An active SSH connection.
    command: str
        The command to run remotely.

    Returns
    -------
    list
        Lines of output produced by the command.
    """
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.readlines()
        return output
    except paramiko.SSHException as error:
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(error)}")

class ServerCommandRequest(BaseModel):
    server_name: str
    command: str

class CommandOutput(BaseModel):
    output: list[str]

@app.post(
    "/ssh_execute/server_command",
    response_model=CommandOutput,
    dependencies=[Depends(get_api_key)],
)
def execute_server_command(
    request: ServerCommandRequest, db: Session = Depends(get_db)
):
    """Execute a shell command on the specified server via SSH."""
    try:
        with connect_to_ssh(request.server_name, db) as ssh_client:
            output = execute_remote_command(ssh_client, request.command)
        return CommandOutput(output=output)
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(error)}")


# added Jan 28 2025
@app.post("/ssh_execute/server_command_testing", dependencies=[Depends(get_api_key)])
def execute_server_command(request: ServerCommandRequest):
    try:
        ssh_client = session_manager.get_session(request.server_name)
        output = execute_remote_command(ssh_client, request.command)
        return {"output": output}
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(error)}")



from fastapi import Body

@app.post("/files/manage")
async def manage_file(filename: str = Body(...), content: str = Body(...)):
    """
    Creates a new file or updates an existing one with the provided content.
    :param filename: Name of the file to create or update.
    :param content: Content to write into the file.
    :return: A message indicating success or failure.
    """
    # Define the path where the file will be located. Adjust as needed.
    file_path = f"./{filename}"  # Adjust the path as per your directory structure

    try:
        # Append content to the file (creates a new file if it doesn't exist)
        with open(file_path, 'a') as file:
            file.write(content)
        return {"message": f"Content appended to '{filename}' successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PythonScriptRequest(BaseModel):
    script_path: str

@app.post("/execute/python_script", dependencies=[Depends(get_api_key)])
def execute_python_script(request: PythonScriptRequest):
    try:
        # Execute the specified Python script
        result = subprocess.run(
            ["python", request.script_path],
            text=True,
            capture_output=True,
            check=True)
        return {
            "stdout": result.stdout.split('\n'),
            "stderr": result.stderr.split('\n')
        }
    except subprocess.CalledProcessError as e:
        # If the script execution fails, capture the output and return as error detail
        return {
            "error": "Command execution failed",
            "stdout": e.stdout.split('\n'),
            "stderr": e.stderr.split('\n')
        }

@app.get("/ssh_execute/list_sessions", dependencies=[Depends(get_api_key)])
def list_open_sessions():
    """
    Lists all open SSH sessions.
    """
    try:
        return {"open_sessions": session_manager.get_open_sessions()}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(error)}")

@app.get("/servers/list", dependencies=[Depends(get_api_key)])
def list_servers():
    """
    Returns a list of available servers.
    """
    return {"servers": list(servers.keys())}

class RenameServerRequest(BaseModel):
    old_name: str
    new_name: str

@app.post("/servers/rename", dependencies=[Depends(get_api_key)])
def rename_server(request: RenameServerRequest):
    """
    Renames a server configuration.
    """
    if request.old_name not in servers:
        raise HTTPException(status_code=404, detail="Server not found")
    if request.new_name in servers:
        raise HTTPException(status_code=400, detail="New server name already exists")

    servers[request.new_name] = servers.pop(request.old_name)
    save_server_configs(servers)
    return {"message": f"Server '{request.old_name}' renamed to '{request.new_name}' successfully."}


@app.get("/healthz")
def healthz(db: Session = Depends(get_db)):
    """Ping all registered servers and report their reachability, hostname, and uptime."""
    host_status = {}
    for name, config in servers.items():
        # First, ping the server to check for reachability
        reachable = ping_vps(config["hostname"])
        host_status[name] = {"ping_reachable": reachable}

        # Always attempt to connect via SSH to get hostname and uptime
        try:
            with connect_to_ssh(name, db) as ssh_client:
                hostname_output = execute_remote_command(ssh_client, "hostname")
                uptime_output = execute_remote_command(ssh_client, "uptime -p")

                host_status[name]["ssh_successful"] = True
                host_status[name]["hostname"] = hostname_output[0].strip() if hostname_output else "N/A"
                host_status[name]["uptime"] = uptime_output[0].strip() if uptime_output else "N/A"

        except FileNotFoundError as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"SSH key file not found: {str(e)}"
        except PermissionError as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"SSH key permission denied: {str(e)}"
        except paramiko.AuthenticationException as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"SSH authentication failed: {str(e)}"
        except paramiko.SSHException as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"SSH connection error: {str(e)}"
        except HTTPException as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"HTTP error: {e.detail}"
        except Exception as e:
            host_status[name]["ssh_successful"] = False
            host_status[name]["error"] = f"Unexpected error: {str(e)}"

    # Overall status is OK if all hosts were successfully contacted via SSH
    overall = "OK" if all(h.get("ssh_successful") for h in host_status.values()) else "NOT_OK"
    return {"status": overall, "hosts": host_status}

# include server inventory router with API key auth
app.include_router(servers_router, dependencies=[Depends(get_api_key)])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
