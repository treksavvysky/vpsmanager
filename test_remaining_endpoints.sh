#!/bin/bash

# Set API key from environment variable or default
AUTH_KEY="${AUTH_KEY:-BBfoTtB5T9XIcEvTEwsByTyAVN8gTdzZ}"

BASE_URL="http://localhost:8971"

print_header() {
  echo -e "\n=================================================="
  echo -e "🔹 $1"
  echo -e "=================================================="
}

# 1. Test /execute/container_bash_command
print_header "POST /execute/container_bash_command"
curl -s -X POST "$BASE_URL/execute/container_bash_command" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"command": "echo Hello from container"}'

# 2. Test /execute/python_script
print_header "POST /execute/python_script"
curl -s -X POST "$BASE_URL/execute/python_script" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"script_path": "example_python.py"}'

# 3. Test /ssh_execute/server_command_testing
print_header "POST /ssh_execute/server_command_testing"
curl -s -X POST "$BASE_URL/ssh_execute/server_command_testing" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"server_name": "server3", "command": "uptime"}'

# 4. Test /ssh_execute/list_sessions
print_header "GET /ssh_execute/list_sessions"
curl -s -X GET "$BASE_URL/ssh_execute/list_sessions" \
  -H "Authorization: $AUTH_KEY"

# 5. Test /files/manage
print_header "POST /files/manage"
curl -s -X POST "$BASE_URL/files/manage" \
  -H "Authorization: $AUTH_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename": "test_results.log", "content": "Test completed successfully.\n"}'

echo -e "\n✅ All tests complete.\n"
