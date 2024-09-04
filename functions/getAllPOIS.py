import requests
from constants import url

def getAllPois (token):
    
    graphql_query_getAllPois = """
        query GetAllPois {
            pois(sort: "createdAt:desc", pagination: { limit: -1 }) {
            data {
                id
                attributes {
                name
                latitude
                longitude
                }
            }
            }
        }
    """
    
    payload = {
        "query": graphql_query_getAllPois
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        json_response = response.json()
        return json_response
    
    else:
        print("Failed to execute GraphQL query. Status code:", response.status_code)
        print("Response:", response.text)
        return None
    
    