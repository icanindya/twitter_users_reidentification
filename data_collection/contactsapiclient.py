'''
Provides ContactsApiClient class that supports 
1. creating individual contact
2. deleting individual contact
3. deleting all contacts
in Google Contacts. 
'''

import time

import gdata.contacts.client
import gdata.contacts.data
import gdata.data
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow


class ContactsApiClient:

    def __init__(self, client_id, client_secret, storage_path):

        FLOW = OAuth2WebServerFlow(
            client_id=client_id,
            client_secret=client_secret,
            scope='https://www.googleapis.com/auth/contacts',
            user_agent='TwitterData/v10')

        storage = Storage(storage_path)
        credentials = storage.get()
        if credentials is None or credentials.invalid == True:
            credentials = run_flow(FLOW, storage)

        auth2token = gdata.gauth.OAuth2TokenFromCredentials(credentials)
        self.gd_client = gdata.contacts.client.ContactsClient(source='TwitterData')
        auth2token.authorize(self.gd_client)

    def create_contact(self, first_name, last_name, full_name, email, phone):

        new_contact = gdata.contacts.data.ContactEntry()

        new_contact.name = gdata.data.Name(given_name=gdata.data.GivenName(text=first_name),
                                           family_name=gdata.data.FamilyName(text=last_name),
                                           full_name=gdata.data.FullName(text=full_name))

        new_contact.email.append(gdata.data.Email(address=email,
                                                  rel=gdata.data.HOME_REL))

        new_contact.phone_number.append(gdata.data.PhoneNumber(text=phone,
                                                               rel=gdata.data.HOME_REL))

        error = True
        while error:
            try:
                # Send the contact data to the server.
                contact_entry = self.gd_client.CreateContact(new_contact)
                contact_id = contact_entry.id.text.split('/')[-1]
                print("Created contact {}: {}.".format(contact_id, contact_entry.name.full_name.text))
                error = False
                return contact_entry

            except Exception as e:
                print('Error creating contact: {}.'.format(str(e)))
                time.sleep(3)

    def delete_contact(self, contact_entry):

        contact_id = contact_entry.id.text.split('/')[-1]
        contact_url = 'https://www.google.com/m8/feeds/contacts/default/full/{}'.format(contact_id)
        contact = self.gd_client.GetContact(contact_url)

        error = True
        while error:
            try:
                self.gd_client.Delete(contact)
                print('Deteted contact {}: {}.'.format(contact_id, contact_entry.name.full_name.text))
                error = False
            except gdata.client.RequestError as e:
                if e.status == 412:
                    print('Error deleting contact: etags mismatch - handle the error.')
                else:
                    print('Error deleting contact: {}'.format(e.message))
                time.sleep(3)

    def delete_all_contacts(self):

        query = gdata.contacts.client.ContactsQuery()
        query.max_results = 10000000
        feed = self.gd_client.GetContacts(q=query)
        for contact_entry in feed.entry:
            self.delete_contact(contact_entry)


if __name__ == '__main__':
    con_client = ContactsApiClient()
