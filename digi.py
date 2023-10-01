import urllib3

# Disable warning for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = 'https://tiny.cc/digi-'
num_episodes = 54

# Generate the list of URLs
l = [base_url + str(i).zfill(2) for i in range(1, num_episodes + 1)]

http = urllib3.PoolManager()

# Set a common user agent to mimic browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

google_drive_links = []

for url in l:
    response = http.request('GET', url, headers=headers, redirect=True)
    # print the final redirected URL
    print(response.geturl())
    if 'drive.google.com' in response.geturl():
        google_drive_links.append(response.geturl())

google_drive_new_links = []

for link in google_drive_links:
    link = link.replace('preview', 'view')
    google_drive_new_links.append(link)

print(google_drive_new_links)

import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
from googleapiclient.http import MediaIoBaseDownload

# Step 1: Authentication and setup
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)

# Step 2: Download files
for drive_link in google_drive_new_links:
    # Extract file ID from link
    file_id = drive_link.split('/')[-2]
    
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Downloaded {int(status.progress() * 100)}%.")

    with open(f'{file_id}.mp4', 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

print("Downloads completed.")
