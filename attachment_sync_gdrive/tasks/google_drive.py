# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import httplib2
from io import BytesIO
from googleapiclient import discovery
from oauth2client.client import AccessTokenCredentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from odoo.tools.mimetypes import guess_mimetype

FOLDER = 'application/vnd.google-apps.folder'


class GoogleDriveTask:
    _key = 'google_drive'
    _name = 'GDRIVE'
    _synchronize_type = None
    _default_port = False
    _hide_login = True
    _hide_password = True
    _hide_port = True
    _hide_address = True

    def __init__(self, access_token):
        google_credentials = AccessTokenCredentials(access_token,
                                                    'my-user-agent/1.0')
        google_http = httplib2.Http()
        google_http = google_credentials.authorize(google_http)
        google_drive = discovery.build('drive', 'v3', http=google_http,
                                       cache_discovery=False)
        self.conn = google_drive.files()

    def setcontents(self, path, data=None):
        """Use the google drive MediaIoBaseUpload"""
        drive_client = self.conn
        mimetype = guess_mimetype(data)
        fh = BytesIO(data)
        media_body = MediaIoBaseUpload(fh, chunksize=-1, mimetype=mimetype,
                                       resumable=True)

        if path.startswith('/'):  # Just incase folder_path starts with "/"
            path = path[1:]
        file_name = path.split('/', 1)[1]
        # construct upload kwargs
        create_kwargs = {
            'body': {
                'name': file_name  # Get the last bit, ignore dirs
            },
            'media_body': media_body,
            'fields': 'id'
        }

        def iterfiles(name=None, is_folder=True, parent=None,
                      order_by='folder,name,createdTime'):
            q = []
            if name is not None:
                q.append("name = '%s'" % name.replace("'", "\\'"))
            if is_folder is not None:
                q.append(
                    "mimeType %s '%s'" % ('=' if is_folder else '!=', FOLDER))
            if parent is not None:
                q.append("'%s' in parents" % parent.replace("'", "\\'"))
            params = {'pageToken': None, 'orderBy': order_by}
            if q:
                q.append("trashed = false")  # skip trash
                params['q'] = ' and '.join(q)
            while True:
                response = drive_client.list(**params).execute()
                for f in response['files']:
                    yield f
                try:
                    params['pageToken'] = response['nextPageToken']
                except KeyError:
                    return

        folder_name = path.split('/')[0]
        folder_details = list(iterfiles(folder_name))
        if folder_details and 'id' in folder_details[0]:
            folder_id = folder_details[0].get('id')
            drive_space = folder_id
        else:
            # Create a new folder and obtain the id
            file_metadata = {
                'name': folder_name,
                'mimeType': FOLDER
            }
            new_folder = drive_client.create(
                body=file_metadata, fields='id').execute()
            folder_id = new_folder.get('id')
            drive_space = folder_id

        # TODO: save folder id for subsequent uploads, dont' search again
        create_kwargs['body']['parents'] = [drive_space]

        # send create request
        file = drive_client.create(**create_kwargs).execute()
        file_id = file.get('id')

        return file_id

    @staticmethod
    def connect(location):
        conn = GoogleDriveTask(location._get_access_token())
        return conn
