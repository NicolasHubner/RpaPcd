import requests
from constants import url

def login_user(username, password):
    # GraphQL endpoint URL

    # GraphQL mutation for login
    graphql_mutation = f"""
    mutation LoginUser {{
      login(input: {{
        identifier: "{username}",
        password: "{password}"
      }}) {{
        jwt
        user {{
          id
          username
          email
        }}
      }}
    }}
    """

#     # Headers with the Content-Type set to application/json
    headers = {
        "Content-Type": "application/json",
        # Add any other headers as needed
    }

#     # Create the payload for the POST request
    payload = {
        "query": graphql_mutation
    }

#     # Make the POST request
    response = requests.post(url, json=payload, headers=headers)

#     # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        json_response = response.json()
        return json_response
    else:
        print("Failed to execute GraphQL mutation. Status code:", response.status_code)
        print("Response:", response.text)
        return None
    
