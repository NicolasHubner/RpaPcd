from datetime import datetime, time, timedelta
import json
import math
from functions.createPnae import createPnae
from functions.getAllFlights import getAllFlights
from functions.getAllPOIS import getAllPois
from functions.getAllPnaes import getAllPnaes
from functions.loginUser import login_user

import pandas as pd

from functions.updatePnae import updatePnae

google_sheets_link = "https://docs.google.com/spreadsheets/d/1b4apxtAY6HUKYmGr1JFwZ-fOxwL16gKQGVch-_-F7_Q/edit?pli=1#gid=1738160815"

document_key = google_sheets_link.split("/d/")[-1].split("/")[0]

excel_url = f"https://docs.google.com/spreadsheets/d/{document_key}/export?format=xlsx"

df = pd.read_excel(excel_url, sheet_name="HCC")

columns = ['DATA', 'TURNO', 'Chegada\nSaída', 'Previsto', 'VOO', 'ORIGEM  ', 'STA',
           'ETA ', 'Posição \nProg', 'Portão', 'Nome completo', 'Voo de Conexão',
           'Sigla', 'STD', 'Serviço 1', 'Serviço 2', 'Colaborador  que solicitou ',
           'Check  Orbital', 'OBSERVAÇÕES', 'Acionamento',
           'Funcionário que realizará o auxílio', 'Início do Auxílio',
           'Fim do Auxílio', 'Honrou ', 'AMBULIFT',
           'Ativado Atendimento Orgânico?']

df.rename(columns=lambda x: x.strip().replace('\n', ''), inplace=True)

selected_columns = ['VOO', 'TURNO', 'ChegadaSaída', 'Posição Prog', 'Portão', 'Nome completo', 'DATA', 'STA', 'ETA', 'STD', 'Voo de Conexão', 'Sigla',  'Serviço 1', 'Serviço 2', 'Previsto']

selected_df = df[selected_columns]

username = "admin@admin.com"
password = "Global@#robos@#"
response = login_user(username, password)

token = response["data"]["login"]["jwt"]

if response:
    print("JWT Token:", response["data"]["login"]["jwt"])
    user_data = response["data"]["login"]["user"]
    print("User ID:", user_data["id"])
    print("Username:", user_data["username"])
    print("Email:", user_data["email"])


# We are not using this function anymore because the names from POIS are not the same from PNAES
# all_pois= getAllPois(token)

all_flights = getAllFlights(token)

all_pnaes = getAllPnaes(token)

# jsonFormat = json.dumps(all_pnaes, indent=1, ensure_ascii=False)
# print(jsonFormat)

# exit()

def ConvertStdEtaToTime(stdEta):
    stdEta_formatted = None  # Initialize the variable before the try-except blocks
    if stdEta:
        if isinstance(stdEta, (time, datetime)):
            # If stdEta is already a datetime.time or datetime.datetime object
            stdEta_formatted = stdEta.strftime('%H:%M:%S.000')
        elif isinstance(stdEta, str):
            try:
                # Try parsing with %H:%M:%S format
                stdEta_datetime = datetime.strptime(stdEta, '%H:%M:%S')
                stdEta_formatted = stdEta_datetime.strftime('%H:%M:%S.000')
            except ValueError:
                try:
                    # If the above fails, try parsing with %H:%M format
                    stdEta_datetime = datetime.strptime(stdEta, '%H:%M')
                    stdEta_formatted = stdEta_datetime.strftime('%H:%M:%S.000')
                except ValueError:
                    # Handle the case where neither format is valid
                    print("Invalid time format")
                    return None  # Add a return statement here if needed
    return stdEta_formatted

def VerifyServiceTypeExist(service1, service2):
    if service1 == 'TEEN' or service2 == 'TEEN':
        return False
    elif pd.isna(service1) and pd.isna(service2):
        return False
    else:
        return True
    

def verifyIfExistPnae(flight_number, passenger_name, flight_date):
    if all_pnaes:
        try:
            pnae = next((item for item in all_pnaes if
             str(item["attributes"]["flightNumber"]) == str(flight_number) and 
             item["attributes"]["passengerName"] == str(passenger_name) and 
             item["attributes"]["flightDate"] == str(flight_date) ),None)

            if pnae:
                # print("PNAE found:", pnae)
                return pnae['id']
            else:
                # print("PNAE not found.")
                return False
        except KeyError as e:
            print(f"KeyError: {e}")
            return False
    else:
        print("No PNAEs available.")
        return False


def is_date_in_range(value, start_date, end_date):
    try:
        # Attempt to parse the datetime
        if pd.notna(value) and value != 'NaT':
            parsed_datetime = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
            return start_date <= parsed_datetime <= end_date
        else:
            # Return False for invalid or missing input
            return False
    except ValueError as e:
        # Handle the case where parsing fails
        print(f"Error parsing datetime: {e}")
        return False

def hasNumbers(s):
    return any(char.isdigit() for char in s)

def isNumberConnectionFlight(value):
    if pd.isna(value):
        return True  # Retorna True se o valor é NaN ou None
    elif isinstance(value, (int, float)):
        return True  # Retorna True se o valor é um número
    elif isinstance(value, str):
        return hasNumbers(value)  # Retorna True se a string contém números
    else:
        return False

def convert_timestamp_to_date(timestamp_object):
    try:
        # Convert Timestamp to string
        date_string = timestamp_object.strftime('%Y-%m-%d %H:%M:%S')

        # Convert the string to a datetime object
        input_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

        # Format the datetime object to the desired format without time
        output_date_str = input_date.strftime('%Y-%m-%d')

        return output_date_str

    except AttributeError:
        # Handle the case where timestamp_object is already a string
        try:
            # Convert the string to a datetime object
            input_date = datetime.strptime(timestamp_object, '%Y-%m-%d %H:%M:%S')

            # Format the datetime object to the desired format without time
            output_date_str = input_date.strftime('%Y-%m-%d')

            return output_date_str

        except ValueError:
            # Handle the case where the string does not match the expected format
            print("Error: Invalid timestamp format.")
            return None

# Obtém a data de início (um dia antes da data atual) e a data atual
today = datetime.now()
start_date = today - timedelta(days=1)

if all_flights:
        all_flights_dict = all_flights['data']['flights']['data']

#         all_pois_dict = all_pois['data']['pois']['data']

        for index, row in selected_df.iterrows():
        
            value = row['VOO']
            if not pd.isna(value):
                if isinstance(value, str) and value.strip() != '' and value.isdigit():
                    result = int(value)
                elif isinstance(value, (int, float)):
                    result = int(value)  # Convert to int if it's a float
                else:
                    result = None  # or some default value
            else:
                result = None  # or some default value
                
            isMoreThanOneDay = is_date_in_range(row['DATA'], start_date, today)
            
            if not result and not isMoreThanOneDay:
                continue
            else:
                ##CONVERT TIME TO DATETIME
                timestamp_object = row['DATA']

                # Check if the timestamp_object is NaT (Not a Time)
                if pd.isna(timestamp_object):
                    print("Timestamp is NaT (Not a Time)")
                else:
                    
                    output_date_str = convert_timestamp_to_date(timestamp_object)
                
                    pnae_exists = verifyIfExistPnae(result, row['Nome completo'], output_date_str)
                    
                    if not pnae_exists and result and isMoreThanOneDay and not pd.isna(row['Nome completo']) and VerifyServiceTypeExist(row['Serviço 1'], row['Serviço 2']) and isNumberConnectionFlight(row['Voo de Conexão']) and not pd.isna(row['STA']):
                        createPnae({
                            "token": token,
                            "all_flights": all_flights_dict,
                            "flight_number": result,
                            "chegada_saida": row['ChegadaSaída'],
                            "flight_box": row['Posição Prog'],
                            "flight_gate": row['Portão'],
                            "passenger_name": row['Nome completo'],
                            "flight_date": row['DATA'],
                            "sta": row['STA'],
                            'eta': row['ETA'],
                            'std': row['STD'],
                            "service1": row['Serviço 1'],
                            "service2": row['Serviço 2'],
                            'flight_connection': row['Voo de Conexão'],
                            'sigla': row['Sigla'],
                            'shift': row['TURNO'],
                            'solicitation': row['Previsto'],
                        })

                    elif pnae_exists and result and isMoreThanOneDay and not pd.isna(row['Nome completo']) and VerifyServiceTypeExist(row['Serviço 1'], row['Serviço 2']) and isNumberConnectionFlight(row['Voo de Conexão']):
                        updatePnae(pnae_exists, token, row['Portão'], row['Posição Prog'], row['Serviço 1'], row['Serviço 2'], row['ChegadaSaída'], row['Voo de Conexão'])
