"""
This script tests an API endpoint similar to how a `curl` command would. It handles authorization through an
environment variable loaded from a .env file. The script accepts command-line arguments for the hostname with port,
use HTTPS, method, path, query parameters, and body in JSON format. It logs the requests and the HTTP response to
an "API test log".

Example usage:
    python test_api.py plannedintent.com:8080 POST api/path '{"query_param":"value"}' '{"key":"value"}'

Dependencies:
    - requests
    - python-dotenv
"""

import sys
import requests
import json
from dotenv import load_dotenv
import os
import logging
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='api_test.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def test_api_endpoint(hostname, method, path, query=None, body=None):
    # Extract API key from environment
    api_key = os.getenv('API_KEY')
    if not api_key:
        logging.error('API key not found in .env file.')
        return

    # Prepare request
    url = f'https://{hostname}/{path}'
    if query:
        query_string = urlencode(query)
        url += f'?{query_string}'
    
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

    # Log the request
    logging.info(f'Making {method} request to {url} with body {body} and headers {headers}')

    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body))
        else:
            logging.error('Unsupported HTTP method.')
            return

        # Log the response
        logging.info(f'Response from {url}: {response.status_code} - {response.text}')

        # Output the response
        print(f'Status code: {response.status_code}\nResponse: {response.text}')

    except Exception as e:
        logging.error(f'Error making request to {url}: {e}')
        print(f'Error: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python test_api.py hostname_with_port method path [query as json] [body as json]')
    else:
        hostname_with_port = sys.argv[1]
        method = sys.argv[2]
        path = sys.argv[3]
        query = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        body = json.loads(sys.argv[5]) if len(sys.argv) > 5 else None
        test_api_endpoint(hostname_with_port, method, path, query, body)
