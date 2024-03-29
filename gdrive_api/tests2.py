from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from pprint import pprint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
CREDENTIALS_FOLDER = '../credentials'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credential_dir = CREDENTIALS_FOLDER
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets-creds.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1452hLMZYc0Y9wBHzOk-yZuIJhuX1Pp__TAeHG2y_-M8'

    requests = []

    sheetId = 2092862843

    requests.append({
        "deleteSheet": {
            "sheetId": sheetId
        }
    })

    batch_update_spreadsheet_request_body = {
        'requests': requests,
    }

    # request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=batch_update_spreadsheet_request_body)
    # response = request.execute()

    request = service.spreadsheets().get(spreadsheetId=spreadsheetId)
    response = request.execute()

    for sheet in response['sheets']:
        print(sheet['properties']['title'], sheet['properties']['sheetId'])


if __name__ == '__main__':
    main()
