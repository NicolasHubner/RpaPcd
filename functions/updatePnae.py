import math
import pandas as pd
import requests
from constants import url

def updatePnae(id, token, gate, box, service1, service2,chegada_saida,flight_connection):
    
    # Concatenate services if both exist
    service_type = str(service1) + ' | ' + str(service2) if pd.notna(service1) and pd.notna(service2) else service1 or service2
    
    if chegada_saida == "Chegada":
                
        origin_passenger = gate if not pd.isna(gate) else box if not pd.isna(box) else 'N/A'

        flight_connection_value = flight_connection

        if flight_connection_value is not None:
            try:
                numeric_value = float(flight_connection_value)
                if not math.isnan(numeric_value):
                    destination_passenger = 'SAE'
                else:
                    destination_passenger = 'Desembarque'
            except ValueError:
                # Handle the case where the value cannot be converted to a number
                destination_passenger = 'Desembarque'
        else:
            destination_passenger = 'Desembarque'
    else:
        origin_passenger = 'Embarque'

        if flight_connection:
            destination_passenger = 'SAE'
        else:
            destination_passenger = gate if gate else box if box else 'N/A'
    
    route_passenger = 'Conexao' if destination_passenger == 'SAE' else 'Local'
    
    graphql_query_updatePnae = """
    mutation updateIssue($id: ID!, $issueOrigin: String, $serviceType: String, $issueDestiny: String, $route: String) {
        updateIssue(
            id: $id
            data: {
                issueDestiny: $issueDestiny
                issueOrigin: $issueOrigin
                serviceType: $serviceType
                route: $route
            }
        ) {
            data {
            id
            attributes {
                passengerName
            }
            }
        }
        }
    """
    
    
    
    object_to_update = {
        "id": id,
        'issueDestiny': str(destination_passenger),
        "issueOrigin": str(origin_passenger),
        "serviceType": service_type,
        "route": route_passenger
    }
    
    variables = {
        "id": object_to_update['id'],
        "issueDestiny": object_to_update['issueDestiny'],
        "issueOrigin": object_to_update['issueOrigin'],
        "serviceType": object_to_update['serviceType'],
        "route": object_to_update['route']
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }
    
    payload = {
        'query': graphql_query_updatePnae,
        'variables': variables
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("PNAE updated successfully", response.json())
        return response.json()
    else:
        print("Error", response.status_code, response.text)
        print(payload)
        return None