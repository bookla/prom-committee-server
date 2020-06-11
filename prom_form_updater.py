import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import socket

from google.cloud import firestore, storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'



# Sheets integration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
spreadsheet_id = 'SPID'


def cache_thumbnails():
    client = storage.Client()
    bucket = client.get_bucket("prom-b3bc9.appspot.com")
    blobs = list(bucket.list_blobs())
    thumbnails = {}
    for each_blob in blobs:
        if "@thumbnails" in each_blob.id:
            thumbnails[each_blob.id.replace("prom-b3bc9.appspot.com/", "").split("/")[1]] = each_blob
    return thumbnails


def get_thumbnail_for(file_link, thumbnails):
    file_name = file_link.split("%2F")[1].split("?alt")[0]
    blob_data = thumbnails[file_name]
    return blob_data.public_url


def main():
    db = firestore.Client()
    collection = db.collection(u'students')
    documents = list(collection.list_documents())
    thumbnails = cache_thumbnails()

    range_ = 'Sheet1!A1:U'
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

    #Clear existing data
    clear_values_request_body = {}
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_, body=clear_values_request_body)
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
            images = []
            for each_image in data["imageLinks"]:
                thumbnail_link = get_thumbnail_for(each_image, thumbnails)
                images.append("=HYPERLINK(\"" + each_image + "\", IMAGE(\"" + thumbnail_link + "\"))")
            if "date" in data.keys():
                to_save = [str(data["date"]), data["name"], data["otherName"], data["house"], data["igAcc"], data["missText"],
                           data["embarrassingText"], data["excuseText"], data["adviceText"], data["highlightText"],
                           data["snrQuote"]]
            else:
                to_save = ["(v2.1.4 or earlier)", data["name"], data["otherName"], data["house"], data["igAcc"], data["missText"],
                           data["embarrassingText"], data["excuseText"], data["adviceText"], data["highlightText"],
                           data["snrQuote"]]
            to_save += images
            request_dataset.append(to_save)
            print(data)

    # Clear placeholder
    clear_values_request_body = {}
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_,
                                                    body=clear_values_request_body)
    request.execute()

    # Add Headers
    header = ["Date Last Edited", "Name", "Other Name", "House", "IG Account", "What will you miss the most about Harrow?",
              "What was your most embarrassing moment?", "What was your best excuse for not doing homework?",
              "Any advice for your younger self?", "What was the highlight of your senior year?",
              "Senior Quote (Can be in karaoke, English or Thai):", "Images: "]

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

    # Finishing up, setting cell sizes and font

    requests = []

    border_request = {
        "updateBorders": {
            "range": {
                "sheetId": 0,
                "startRowIndex": 0,
                "endRowIndex": 200,
                "startColumnIndex": 0,
                "endColumnIndex": 25
            },
            "top": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
            "bottom": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
            "left": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
            "right": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
            "innerHorizontal": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
            "innerVertical": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "red": 0,
                    "green": 0,
                    "blue": 0,
                    "alpha": 1
                }
            },
        }
    }


    requests.append(border_request)


    body = {
        "requests": requests
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body).execute()

    range_b = 'Sheet1!V1:X'

    value_range_body = {
        "values": [["Last Updated : ", str(datetime.datetime.now())], ["Updated by : ", str(socket.gethostname())]]
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_b,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()




