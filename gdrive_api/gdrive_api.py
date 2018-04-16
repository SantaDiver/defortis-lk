from __future__ import print_function

from django.conf import settings
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

class gdriveAPI(object):
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'
    CREDENTIALS_FOLDER = os.path.join(settings.BASE_DIR, 'credentials')

    def __init__(self):
        credentials = self.get_credentials('drive-creds.json')
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build(
            'drive',
            'v3',
            http=http
        )

        credentials = self.get_credentials('sheets-creds.json')
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        self.spr_service = discovery.build(
            'sheets',
            'v4',
            http=http,
            discoveryServiceUrl=discoveryUrl
        )

    def get_credentials(self, file_name):
        credential_dir = self.CREDENTIALS_FOLDER
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, file_name)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            raise Exception('Bad credentials!')
        return credentials

    def download_file(self, file_id, file_name, spreadsheet):
        service = self.service
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

    def upload_file(self, upload_name, file_name, mimetype, parent_id=None):
        service = self.service
        file_metadata = {'name': upload_name}

        if parent_id:
            if type(parent_id) is list:
                file_metadata['parents'] = parent_id
            else:
                file_metadata['parents'] = [parent_id,]

        media = MediaFileUpload(file_name, mimetype=mimetype)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        # print ('File ID: %s' % file.get('id'))
        return file.get('id')

    def upload_spreadsheet(self, upload_name, file_name, parent_id=None):
        service = self.service
        file_metadata = {
            'name': upload_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        if parent_id:
            if type(parent_id) is list:
                file_metadata['parents'] = parent_id
            else:
                file_metadata['parents'] = [parent_id,]

        media = MediaFileUpload(
            file_name,
            mimetype='application/vnd.ms-excel',
            resumable=True,
        )
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')

    def create_folder(self, folder_name, parent_id=None):
        service = self.service
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        if parent_id:
            if type(parent_id) is list:
                folder_metadata['parents'] = parent_id
            else:
                folder_metadata['parents'] = [parent_id,]

        create_folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        return create_folder['id']

    def get_folder_contents(self, folder_id):
        service = self.service
        page_token = None
        result = []
        while True:
            try:
                response = service.files().list(
                    q="trashed != True and \
                    parents in %r" % folder_id,

                    spaces='drive',
                    fields='nextPageToken, files(id, name, modifiedTime, webContentLink)',
                    pageToken=page_token
                ).execute()
            except:
                return []
            result += response.get('files', [])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return result

    def give_permissions(self, file_id, user_permissions):
        if not user_permissions:
            return
        service = self.service

        def callback(request_id, response, exception):
            if exception:
                # Handle error
                # print (exception)
                pass
            else:
                # print ("Permission Id: %s" % response.get('id'))
                pass

        # batch = service.new_batch_http_request(callback=callback)
        batch = service.new_batch_http_request()
        if not type(user_permissions) is list:
            user_permissions = [user_permissions]
        for user_permission in user_permissions:
            batch.add(service.permissions().create(
                    fileId=file_id,
                    body=user_permission,
                    fields='id',
            ))
        batch.execute()

    def get_permited_emails(self, file_id):
        service = self.service
        page_token = None
        result = []
        while True:
            try:
                response = service.permissions().list(
                    fileId = file_id,
                    fields='nextPageToken, permissions(emailAddress)',
                    pageToken=page_token
                ).execute()
            except:
                return []
            for permission in response.get('permissions', []):
                if 'emailAddress' in permission:
                    result.append(permission['emailAddress'])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return result

    def get_start_changes_token(self):
        service = self.service
        response = service.changes().getStartPageToken().execute()
        return response.get('startPageToken')

    def get_changes(self, page_token):
        service = self.service
        saved_start_page_token = None
        result = []
        while page_token is not None:
            response = service.changes().list(
                pageToken=page_token,
                spaces='drive'
            ).execute()
            # for change in response.get('changes'):
            #     # Process change
            #     print ('Change found for file: %s' % change.get('fileId'))
            #     print(change)
            result += response.get('changes', [])
            if 'newStartPageToken' in response:
                # Last page, save this token for the next polling interval
                saved_start_page_token = response.get('newStartPageToken')
            page_token = response.get('nextPageToken')

        return result, saved_start_page_token

    def get_file_by_id(self, file_id):
        service = self.service
        response = service.files().get(
            fileId=file_id,
            fields='id, name, webContentLink'
        ).execute()
        return response

    def split_main_file(self, pobject, sys_val, full_file_name):
        service = self.service

        file_id = pobject.main_file
        self.download_file(file_id, full_file_name, False)

        id = self.upload_spreadsheet(
            upload_name=full_file_name,
            file_name=full_file_name,
            parent_id=sys_val.hidden_folder
        )

        batch = service.new_batch_http_request()
        user_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        batch.add(service.permissions().create(
                fileId=id,
                body=user_permission,
                fields='id',
        ))
        batch.execute()

        spr_service = self.spr_service

        request = spr_service.spreadsheets().get(spreadsheetId=id)
        response = request.execute()

        result = []
        for sheet in response['sheets']:
            download_link = ('https://docs.google.com/spreadsheets/d/%s/export?'
                'format=pdf&'
                'portrait=false&'
                'gid=%s'
            ) % (id, sheet['properties']['sheetId'])
            result.append({
                'name' : full_file_name.split('.')[0] +
                    '-'+sheet['properties']['title'],
                'download_link' : download_link,
            })

        os.remove(full_file_name)
        return result, id

    def delete_files(self, ids):
        service = self.service
        for id in ids:
            service.files().delete(fileId=id).execute()
