from datetime import datetime, timedelta
import requests
from constants import url

# Get all flight international that Orbital has in the next 24 hours

def getAllFlights(token):
    #GraphQl Endpoint Url
    
    #if need to get international flights, add this line in the query
    # isInternational: { eq: $isInternational }
    # and this line in the variables
    # "isInternational": {
    #     "eq": objectToCreate['isInternational']
    # }
    # and isInternational: BooleanFilterInput
    
    graphql_query_template = '''
        query flights(
            $pageSize: Int
            $fromDate: DateTime
            $toDate: DateTime
            ) {
            flights(
                pagination: { page: 1, pageSize: $pageSize }
                filters: {
                    createdAt: { gte: $fromDate, lte: $toDate }
                }
            ) {
                data {
                    id
                    attributes {
                        flightNumber
                        flightDate
                    }
                }
            }
        }
    '''
    
    date_today = datetime.today()
    
    date_today_minus_1 = date_today - timedelta(days= 2)
    
    date_today_plus_2 = date_today + timedelta(days=2)
    
    date_today_formated = date_today_minus_1.strftime('%Y-%m-%dT%H:%M:00Z')
    
    date_today_plus_2_formated = date_today_plus_2.strftime('%Y-%m-%dT%H:%M:00Z')
    
    objectToCreate = {
        "pageSize": 1000,
        "fromDate": date_today_formated,
        "toDate": date_today_plus_2_formated,
        # "isInternational": True,
    }
    
    variables = {
        "pageSize": objectToCreate['pageSize'],
        "fromDate": objectToCreate['fromDate'],
        "toDate": objectToCreate['toDate'],
        # "isInternational": {
        #     "eq": objectToCreate['isInternational']
        # }
    }

    # Combine the query and variables for the POST request
    payload = {
        "query": graphql_query_template,
        "variables": variables
    }

    headersAuthorization = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, json=payload, headers=headersAuthorization)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code, response.text)
        return None

