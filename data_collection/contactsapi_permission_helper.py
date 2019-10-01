'''
Helps contactsapiclient to acquire permission to read 
and write to Google Contacts.
'''

import os

import google_credentials as gcred
from contactsapiclient import ContactsApiClient

STORAGE_DIR = r'D:\Data\Linkage\FL\FL18\auth_tokens'
GOOGLE_USERNAME = ''
storage_path = os.path.join(STORAGE_DIR, '{}.auth'.format(GOOGLE_USERNAME))
client = ContactsApiClient(gcred.client_ids[GOOGLE_USERNAME], gcred.client_secrets[GOOGLE_USERNAME], storage_path)
