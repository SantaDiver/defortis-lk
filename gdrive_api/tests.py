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

import xlrd
from xlutils.copy import copy

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
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

def get_credentials():
    home_dir = os.path.expanduser('.')
    credential_dir = os.path.join(home_dir, 'credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

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

    # return

    # results = service.files().list(
    #     pageSize=3,fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print('{0} ({1})'.format(item['name'], item['id']))

    # page_token = None
    # while True:
    #     response = service.files().list(
    #         q="name contains 'test2' and + \
    #         mimeType = 'application/vnd.google-apps.folder'and \
    #         trashed != True",
    #
    #         spaces='drive',
    #         fields='nextPageToken, files(id, name, modifiedTime, webContentLink)',
    #         pageToken=page_token
    #     ).execute()
    #     response = service.files().list(
    #         q='mimeType = "application/vnd.google-apps.document" and \
    #             parents in "0BwbYJirXwPy5bzZtUXN2dVU5WjA"',
    #         spaces='drive',
    #         fields='nextPageToken, files(id, name, modifiedTime, webContentLink)',
    #         pageToken=page_token,
    #     ).execute()
    #     r = service.files().get(
    #         fileId=file.get('id')
    #     ).execute()
    #     for file in response.get('files', []):
    #         # Process change
    #         print (('Found file: %s (%s)') % (file.get('name'), file.get('id')))
    #         pprint(file.get('webContentLink'))
    #     page_token = response.get('nextPageToken', None)
    #     if page_token is None:
    #         break

    # folder_metadata = {
    #     'name': 'Корневая директория',
    #     # 'parents': ['0BwbYJirXwPy5bzZtUXN2dVU5WjA'],
    #     'mimeType': 'application/vnd.google-apps.folder',
    # }
    # create_folder = service.files().create(body=folder_metadata, fields='id').execute()
    # pprint(create_folder)

    full_file_name = 'some.xls'
    file_id = '18-rnNJNYKjlNtqZIBeFKgPh1oXbzUw8c'

    download_file(service, file_id, full_file_name, False)
    wb = xlrd.open_workbook(full_file_name, on_demand=True)

    targetdir = ('./') #where you want your new files
    for sheet in wb.sheets(): #cycles through each sheet in each workbook
        newwb = copy(wb) #makes a temp copy of that book
        newwb._Workbook__worksheets = [ worksheet for worksheet in \
            newwb._Workbook__worksheets if worksheet.name == sheet.name ]
        #brute force, but strips away all other sheets apart from the sheet being looked at
        part_name = targetdir + full_file_name.split('.')[0] + '-' + sheet.name
        part_xls_name = part_name + '.xls'
        newwb.save(part_xls_name)
        #saves each sheet as the original file name plus the sheet name
        id = upload_spreadsheet(service, part_name, part_xls_name)

        pdf_name = part_name + '.pdf'
        download_file(service, id, pdf_name, True)
        pdf_id = upload_file(service, part_name.split('/')[1], pdf_name, 'application/pdf')

        os.remove(pdf_name)
        os.remove(part_name + '.xls')
        service.files().delete(fileId=id).execute()

        batch = service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        batch.add(service.permissions().create(
                fileId=pdf_id,
                body=user_permission,
                fields='id',
        ))
        batch.execute()

        response = service.files().get(
            fileId=pdf_id,
            fields='id, name, webContentLink'
        ).execute()

        pprint(response)

    os.remove(full_file_name)

    # response = drive_service.changes().getStartPageToken().execute()
    # print 'Start token: %s' % response.get('startPageToken')

    # page_token = '688457'
    # while page_token is not None:
    #     response = service.changes().list(pageToken=page_token,
    #                                         spaces='drive').execute()
    #     for change in response.get('changes'):
    #         # Process change
    #         print ('Change found for file: %s' % change.get('fileId'))
    #     if 'newStartPageToken' in response:
    #         # Last page, save this token for the next polling interval
    #         saved_start_page_token = response.get('newStartPageToken')
    #         pprint(saved_start_page_token)
    #     page_token = response.get('nextPageToken')



if __name__ == '__main__':
    main()
