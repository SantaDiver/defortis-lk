from __future__ import print_function
import httplib2
import os
from pprint import pprint

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
import io
from apiclient.http import MediaIoBaseDownload

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    pprint('----------flags------------')
    pprint(flags)
    pprint('----------end of flags------------')
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

def get_credentials():
    home_dir = os.path.expanduser('..')
    credential_dir = os.path.join(home_dir, 'credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-creds.json')

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

def download_file(service, file_id, file_name, spreadsheet):
    with open(file_name, 'wb') as fh:
        file_id = file_id
        if spreadsheet:
            request = service.files().export_media(fileId=file_id,
                                                    mimeType='application/pdf')
        # application/pdf
        # application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        else:
            request = service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print ("Download %d%%." % int(status.progress() * 100))

def upload_spreadsheet(service, upload_name, file_name):
    file_metadata = {
        'name': upload_name,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    media = MediaFileUpload(
        file_name,
        mimetype='application/vnd.ms-excel',
        # mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        resumable=True,
    )
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    # print ('File ID: %s' % file.get('id'))
    return file.get('id')

def upload_file(service, upload_name, file_name, mimetype):
    file_metadata = {'name': upload_name}
    media = MediaFileUpload(file_name, mimetype=mimetype)
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    # print ('File ID: %s' % file.get('id'))
    return file.get('id')

def callback(request_id, response, exception):
    if exception:
        # Handle error
        print (exception)
    else:
        print ("Permission Id: %s" % response.get('id'))

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    file_id = '1452hLMZYc0Y9wBHzOk-yZuIJhuX1Pp__TAeHG2y_-M8'


if __name__ == '__main__':
    main()
