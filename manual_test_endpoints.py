import requests
import json

api_key = "BBfoTtB5T9XIcEvTEwsByTyAVN8gTdzZ"
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

def test_list_servers():
    response = requests.get("http://localhost:8000/servers/list", headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_rename_server():
    payload = {
        "old_name": "server1",
        "new_name": "plannedintent-dev"
    }
    response = requests.post("http://localhost:8000/servers/rename", headers=headers, data=json.dumps(payload))
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_list_servers()
    test_rename_server()
    test_list_servers()
