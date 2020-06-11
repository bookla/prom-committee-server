import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import string

from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'MY CRED'


def put_votes_on_sheets(range, votes):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    spreadsheet_id = 'SPID'
    range_ = 'Sheet1!' + range

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

    # Clear existing data
    clear_values_request_body = {}
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_,
                                                    body=clear_values_request_body)
    request.execute()

    value_input_option = 'USER_ENTERED'
    insert_data_option = 'OVERWRITE'

    value_range_body = {
        "values": votes
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    request.execute()


def load_and_print_votes(mute):
    vote_descriptions = {"igFamous": "Most likely to be Instagram Famous",
                         "married": "Most likely to get married",
                         "president": "Most likely to become president",
                         "travelTheWorld": "Most likely to travel the world",
                         "bestDressed": "Best Dressed",
                         "bestBromance": "Best Bromance",
                         "bestWomance": "Best Womance",
                         "bestSmile": "Best Smile",
                         "classClown": "Class Clown",
                         "skipUni": "Most likely to skip university",
                         "bestCouple": "Best Couple",
                         "heartBreaker": "Heartbreaker",
                         "billionaire": "Most likely to become a billionaire",
                         "arrested": "Most likely to get arrested",
                         "flirt": "Most likely to flirt their way out of a parking ticket"
                         }


    db = firestore.Client()
    collection = db.collection(u'vote')
    documents = list(collection.list_documents())
    votes = {}
    data_dump = {}
    for eachDoc in documents:
        if eachDoc.id == "NqLey2EzBa3F2QiycFrX":
            pass
        else:
            data = eachDoc.get().to_dict()
            data_dump[eachDoc.id] = data
            votes[eachDoc.id] = sorted(data, key=data.get, reverse=True)

    if not mute:
        print("Sorted Votes:")
    cat_num = 0
    for cat in sorted(votes.keys()):
        print(str(round(cat_num/len(votes.keys())*100)) + "% Complete")
        val = votes[cat]
        cat_data = [[vote_descriptions[cat]]]
        if not mute:
            print(vote_descriptions[cat] + " (" + cat + ") :")
        for eachVoted in val:
            temp_data = [eachVoted, data_dump[cat][eachVoted]]
            cat_data.append(temp_data)
            if not mute:
                print(eachVoted + ": " + str(data_dump[cat][eachVoted]))
        strings = list(string.ascii_uppercase) + ["A" + char for char in list(string.ascii_uppercase)]
        char_one = strings[(3 * cat_num)]
        char_two = strings[(3 * cat_num) + 1]
        put_votes_on_sheets(char_one + "1" + ":" + char_two + "200", cat_data)
        cat_num += 1
        if not mute:
            print("-------\n\n\n")





