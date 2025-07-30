#!/bin/bash

# Load the API key from environment variable
AUTH_KEY="${AUTH_KEY}"

# Target API endpoint (change as needed)
URL="http://localhost:8971/your-endpoint"

# Run the test with curl
curl -X GET "$URL" \
  -H "Authorization: Bearer $AUTH_KEY" \
  -H "Content-Type: application/json"
#!/bin/bash

# Use hardcoded API key until .env loading is fixed
AUTH_KEY="BBfoTtB5T9XIcEvTEwsByTyAVN8gTdzZ"

# Target API endpoint (change as needed)
URL="http://localhost:8971/your-endpoint"

# Run the test with curl
curl -X GET "$URL" \
  -H "Authorization: Bearer $AUTH_KEY" \
  -H "Content-Type: application/json"#!/bin/bash

# Use hardcoded API key until .env support is fixed
AUTH_KEY="BBfoTtB5T9XIcEvTEwsByTyAVN8gTdzZ"

# Function to make a GET request with the API key
make_get_request() {
  local endpoint=$1
  echo -e "\nTesting GET $endpoint"
  curl -s -X GET "http://localhost:8971$endpoint" \
    -H "Authorization: $AUTH_KEY" \
    -H "Content-Type: application/json"
  echo -e "\n--------------------------------------------------"
}

# Test public endpoint
make_get_request "/"

# Test protected endpoints
make_get_request "/vps/status"
make_get_request "/servers/list"

# NOTE: /servers/rename and /ssh_execute/server_command are POST endpoints, not GET.
# We'll include dummy test payloads for them below.

# Test /servers/rename (POST)
echo -e "\nTesting POST /servers/rename"
curl -s -X POST "http://localhost:8971/servers/rename" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"old_name": "plannedinent-dev", "new_name": "plannedintent-dev"}'

# Test /ssh_execute/server_command (POST)
echo -e "\n--------------------------------------------------"
echo -e "\nTesting POST /ssh_execute/server_command"
curl -s -X POST "http://localhost:8971/ssh_execute/server_command" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"server_name": "plannedintent-dev", "command": "ls"}'

echo -e "\n--------------------------------------------------"
echo -e "\nAll tests complete."
