from datetime import datetime, time
import json
import requests
import pandas as pd
import math
from constants import url

def getStaEtaPassenger(items):
    sta_eta_passenger = items['eta'] if pd.notna(items['eta']) else items['sta'] if pd.notna(items['sta']) else None

    if sta_eta_passenger is None:
        print("STA/ETA is None")
        return None  # Return None in case of None input

    sta_eta_formatted = None  # Initialize sta_eta_formatted outside the try-except blocks

    if isinstance(sta_eta_passenger, (time, datetime)):
        # If sta_eta_passenger is already a datetime.time or datetime.datetime object
        sta_eta_formatted = sta_eta_passenger.strftime('%H:%M:%S.000')
    elif isinstance(sta_eta_passenger, str):
        try:
            # Try parsing with %H:%M:%S format
            sta_eta_passenger_datetime = datetime.strptime(sta_eta_passenger, '%H:%M:%S')
            sta_eta_formatted = sta_eta_passenger_datetime.strftime('%H:%M:%S.000')
        except ValueError:
            try:
                # If the above fails, try parsing with %H:%M format
                sta_eta_passenger_datetime = datetime.strptime(sta_eta_passenger, '%H:%M')
                sta_eta_formatted = sta_eta_passenger_datetime.strftime('%H:%M:%S.000')
            except ValueError:
                # Handle the case where neither format is valid
                print("Invalid time format")

    return sta_eta_formatted

def createPnae(items):
    timestamp_object = items['flight_date']

    # Check if the timestamp_object is NaT (Not a Time)
    if pd.isna(timestamp_object):
        print("Timestamp is NaT (Not a Time)")
    else:
        # Convert Timestamp to string
        date_string = timestamp_object.strftime('%Y-%m-%d %H:%M:%S')

        # Convert the string to a datetime object
        input_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

        # Format the datetime object to the desired format without time
        output_date_str = input_date.strftime('%Y-%m-%d')
        
        flightId = next((item for item in items['all_flights'] if (str(item["attributes"]["flightNumber"]) == str(items['flight_number'])) and (item["attributes"]["flightDate"] == output_date_str)), None)

        if not flightId:
            print("Flight not found.")
        else:
            if items['chegada_saida'] == "Chegada":
                
                origin_passenger = items['flight_gate'] if pd.notna(items['flight_gate']) else \
                    items['flight_box'] if pd.notna(items['flight_box']) else 'N/A'
                
                flight_connection_value = items['flight_connection']

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

                if items['flight_connection']:
                    destination_passenger = 'SAE'
                else:
                    destination_passenger = items['flight_gate'] if items['flight_gate'] else items['flight_box'] if items['flight_box'] else 'N/A'

            sta_eta_passenger = getStaEtaPassenger(items)

            # Assuming items is a dictionary with keys 'service1' and 'service2'
            service1 = items.get('service1', None)
            service2 = items.get('service2', None)

            # Concatenate services if both exist
            service_type = str(service1) + ' | ' + str(service2) if pd.notna(service1) and pd.notna(service2) else service1 or service2

            graphql_query_createPnae = """
                mutation createIssue(
                    $areaCode: ID!
                    $flightNumber: Long!
                    $flightID: ID
                    $description: String!
                    $passengerName: String!
                    $status: ENUM_ISSUE_STATUS!
                    $flightDate: Date!
                    $stdEta: Time!
                    $flightGate: String!
                    $route: String!
                    $solicitation: String!
                    $serviceType: String!
                    $shift: ENUM_ISSUE_SHIFT!
                    $publishedAt: DateTime
                    $issueOrigin: String
                    $issueDestiny: String
                ) {
                    createIssue(
                        data: {
                            area: $areaCode
                            flightNumber: $flightNumber
                            flight: $flightID
                            description: $description
                            passengerName: $passengerName
                            status: $status
                            flightDate: $flightDate
                            stdEta: $stdEta
                            flightGate: $flightGate
                            route: $route
                            solicitation: $solicitation
                            serviceType: $serviceType
                            shift: $shift
                            publishedAt: $publishedAt
                            issueOrigin: $issueOrigin
                            issueDestiny: $issueDestiny
                        }
                    ) {
                        data {
                            id
                            attributes {
                                passengerName
                                flightNumber
                            }
                        }
                    }
                }
            """

            solicitation_value = items['solicitation']
            
            if solicitation_value == 'Previsto':
                mapped_value = 'Previsto'
            elif solicitation_value == 'Não previsto':
                mapped_value = 'Nao previsto'
            else:
                mapped_value = 'Nao previsto'  # Change this as needed
            
            route_passenger = 'Connection' if destination_passenger == 'SAE' else 'Local'
            
            object_variables = {
                "areaCode": 12, # 12 = PNAE
                "flightNumber": items['flight_number'],
                "description": items['passenger_name'],
                "passengerName": items['passenger_name'],
                "status": "pending",
                "flightDate": output_date_str,
                "stdEta": sta_eta_passenger, # 10:00:00.000 format
                "flightGate": str(origin_passenger),
                "route": route_passenger,
                "solicitation": mapped_value,
                "serviceType": service_type if service_type else "WCHR",
                "shift": items['shift'] if items['shift'] else "N/A",
                "flightID": flightId['id'] if flightId and 'id' in flightId else None,
                'issueOrigin': str(origin_passenger),
                'issueDestiny': str(destination_passenger),
                "publishedAt": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
            
            # formatted_json = json.dumps(object_variables, indent=2)

            # Headers with the Content-Type set to application/json
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {items['token']}"
                # Add any other headers as needed
            }
            
            # Create the payload for the POST request
            payload = {
                "query": graphql_query_createPnae,
                "variables": object_variables
            }
            
            # Make the POST request
            response = requests.post(url, json=payload, headers=headers)
            
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the JSON response
                json_response = response.json()
                print("Pnae created Successufuly:", json_response)
                return json_response
            else:
                print("Failed to execute GraphQL mutation. Status code:", response.status_code)
                print("payload", payload)
                print("Error:", response.text)
                return None
    