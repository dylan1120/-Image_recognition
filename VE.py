from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os, io

SCOPES = 'https://www.googleapis.com/auth/drive'
IMAGEDIR = 'files'

def authorize_api():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return build('drive', 'v3', http=creds.authorize(Http()))

def main():
    drive_service = authorize_api()
    image_list = os.listdir(IMAGEDIR)

    for filename in image_list:
        print('[%s]' % filename)
        print('Uploading... ', end='', flush=True)
        file_metadata = {
            'name': filename,
            'mimeType': 'application/vnd.google-apps.document'
        }
        full_path = os.path.join(IMAGEDIR, filename)
        media = MediaFileUpload(full_path,
            mimetype='image/jpeg',
            resumable=True)
        file = drive_service.files().create(body=file_metadata,
            media_body=media,
            fields='id').execute()
        file_id = file.get('id')
        print('Done')
        print('File ID: %s' % file_id)

        print('Downloading... ', end='', flush=True)
        output_filename = os.path.splitext(filename)[0] + '.txt'
        fh = io.FileIO(output_filename, 'wb')
        request = drive_service.files().export_media(fileId=file_id,
            mimeType='text/plain')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        print('Done')

        drive_service.files().delete(fileId=file_id).execute()

if __name__ == '__main__':
    main()