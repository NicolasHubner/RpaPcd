from datetime import datetime, timedelta
import json
import requests
from constants import url

def getAllPnaes(token):
    
    graphql_query_getAllPnaes = """
        query Issues(
            $areaCode: String
            $fromDate: DateTime
            $toDate: DateTime
            $status: String
    ) {
        issues(
        sort: "flightDate:desc"
        pagination: { limit: -1 }
        filters: {
            status: { eq: $status }
            area: { code: { eq: $areaCode } }
            createdAt: { gte: $fromDate, lte: $toDate }
        }
        ) {
        data {
            id
            attributes {
            shift
            dtEnd
            status
            dtStart
            createdAt
            stdEta
            evidenceDescription
            passengerName
            solicitation
            flightNumber
            issueOrigin
            issueDestiny
            flightDate
            }
        }
        }
    }
  """


#   areaCode from Pnae PNE
    today = datetime.today()
  
    yestarday = today - timedelta(days=2)
    
    tomorrow = today + timedelta(days=1)
    
    tomorrow_formatted = tomorrow.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    yestarday_formatted = yestarday.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    objectToCreate = {
    "areaCode": "PNE",
    "fromDate": yestarday_formatted,
    "toDate": tomorrow_formatted,
    "status": "pending"
  }
  
    variables = {
    "areaCode": objectToCreate["areaCode"],
    "fromDate": objectToCreate["fromDate"],
    "toDate": objectToCreate["toDate"],
    "status": objectToCreate["status"]
  }
    payload = {
        "query": graphql_query_getAllPnaes,
        "variables": variables
    }

    headersAuthorization = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(url, json=payload, headers=headersAuthorization)
    
    if response.status_code == 200:
        json_response = response.json()
        
        # indented_json_string = json.dumps(json_response, indent=2, ensure_ascii=False)
        # print(indented_json_string)
        return json_response["data"]["issues"]["data"]
    
    else:
        print("Failed to execute GraphQL query. Status code:", response.status_code)
        print("Response:", response.text)
        return None