from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import paramiko
import subprocess

from session_manager import SSHSessionManager

load_dotenv()  # Load environment variables from .env file

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

# Update passwords from environment variables
servers["server2"]["password"] = os.getenv('CODEJOURNEY_PASSWORD')
servers["server3"]["password"] = os.getenv('DECLARESUCCESS_PASSWORD')

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != "BBfoTtB5T9XIcEvTEwsByTyAVN8gTdzZ":
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

def connect_to_ssh(server_name):
    """Connects to an SSH server and returns the SSHClient object."""
    if server_name not in servers:
        raise HTTPException(status_code=400, detail="Invalid server name")
    
    server = servers[server_name]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if server["auth_type"] == "key":
            ssh_client.connect(hostname=server["hostname"], username=server["username"], key_filename=server["key_filename"])
        elif server["auth_type"] == "password":
            ssh_client.connect(hostname=server["hostname"], username=server["username"], password=server["password"])
        else:
            raise ValueError("Invalid authentication type")
        return ssh_client
    except paramiko.AuthenticationException:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except paramiko.SSHException as error:
        raise HTTPException(status_code=500, detail=f"SSH connection error: {str(error)}")

def execute_remote_command(ssh_client, command):
    """Executes a command on the remote server and returns the output."""
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.readlines()
        return output
    except paramiko.SSHException as error:
        raise HTTPException(status_code=500, detail=f"Command execution error: {str(error)}")

class ServerCommandRequest(BaseModel):
    server_name: str
    command: str

@app.post("/ssh_execute/server_command", dependencies=[Depends(get_api_key)])
def execute_server_command(request: ServerCommandRequest):
    try:
        with connect_to_ssh(request.server_name) as ssh_client:
            output = execute_remote_command(ssh_client, request.command)
        return {"output": output}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
