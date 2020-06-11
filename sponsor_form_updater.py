import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import socket

from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'



# Sheets integration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheet_id = 'SPID'


def main():
    db = firestore.Client()
    collection = db.collection(u'sponsors')
    documents = list(collection.list_documents())

    range_ = 'Sheet1!A1:F'
    range_clear = 'Sheet1!A1:H'
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('Leaver'):
        with open('Leaver', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('Leaver', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print(values)

    # Clear existing data
    clear_values_request_body = {}
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_clear, body=clear_values_request_body)
    request.execute()

    value_input_option = 'USER_ENTERED'
    insert_data_option = 'OVERWRITE'

    # Insert placeholder
    value_range_body = {
        "values": [["THE SCRIPT IS FETCHING DATA FROM THE DATABASE"]]
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()

    # Fetch Data From Database
    request_dataset = []

    for each_doc in documents:
        if each_doc.id != "Prototype User":
            data = each_doc.get().to_dict()["updateData"]
            image_data = "=IMAGE(\"" + data["imageLink"][0] + "\")"
            to_save = [str(data["date"]), data["companyName"], data["contactEmail"], data["contactPhone"], data["sponsorAmount"], image_data]
            request_dataset.append(to_save)
            print(image_data)
            print(to_save)

    # Clear placeholder
    clear_values_request_body = {}
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_clear,
                                                    body=clear_values_request_body)
    request.execute()

    # Add Headers
    header = ["Date Submitted", "Company Name", "Email", "Phone", "Sponsor Amount", "Image"]
    value_range_body = {
        "values": [header]
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()

    # Write main data

    value_range_body = {
        "values": request_dataset
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()

    # Add updater values

    range_b = 'Sheet1!G1:H'
    value_range_body = {
        "values": [["Last Updated : ", str(datetime.datetime.now())], ["By Server : ", str(socket.gethostname())]]
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_b,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()

