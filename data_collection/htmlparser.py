import os
import re

from bs4 import BeautifulSoup

FL_RECORDS_SPLITS_DIR = r"D:\Data\Linkage\FL\FL18\fl_rec_splits_new"

TW_ACCOUNTS_DIR = r"D:\Data\Linkage\FL\FL18\tw_accounts_new"
TW_ACCOUNTS_PARSED_DIR = r"D:\Data\Linkage\FL\FL18\tw_accounts_parsed_new"

TW_IMPORTS_DIR = r"D:\Data\Linkage\FL\FL18\tw_imports_new"
TW_RUNNING_RECORDS_DIR = r"D:\Data\Linkage\FL\FL18\tw_running_records_new"


def parse_contacts(start, end):
    for i in range(start, end):

        read_file_path = os.path.join(TW_ACCOUNTS_DIR, 'acc_{}.html'.format(i))
        write_file_path = os.path.join(TW_ACCOUNTS_PARSED_DIR, "acc_parsed_{}.txt".format(i))

        with open(read_file_path, 'rb') as html_file:
            soup = BeautifulSoup(html_file, 'lxml')

        matches = soup.find_all('div', class_='content')

        account_list = []

        for match in matches:

            profile = match.a
            bio = match.p

            if profile and bio:
                user_id = profile.get('data-user-id')
                profile_handle = profile.get('href')[1:]

                name_text = profile.strong.text
                name_text = re.sub(r'[^\x00-\x7F]+', ' ', name_text)
                name = re.sub(r'\s+', ' ', name_text).strip()

                tweets_public = 'F' if profile.find('span', text='Protected Tweets') else 'T'

                bio_text = bio.text
                bio_text = re.sub(r'[^\x00-\x7F]+', ' ', bio_text)
                biography = re.sub(r'\s+', ' ', bio_text).strip()

                account_list.append((name, profile_handle, user_id, tweets_public, biography))

        account_list.sort(key=lambda x: x[0].upper())

        with open(write_file_path, 'w') as wf:
            for account_tup in account_list:
                wf.write('\t'.join(list(account_tup)) + '\n')


def parse_imports(start, end):
    for i in range(start, end):

        import_path = os.path.join(TW_IMPORTS_DIR, 'imp_{}.html'.format(i))
        records_path = os.path.join(FL_RECORDS_SPLITS_DIR, "rec_{}.txt".format(i))
        tw_running_records_path = os.path.join(TW_RUNNING_RECORDS_DIR, "tw_running_rec_{}.txt".format(i))

        tw_running_emails = set()

        with open(import_path, "rb") as html_file:
            soup = BeautifulSoup(html_file, 'lxml')

        contacts = soup.find_all("tr", {"data-item-type": "contact"})

        for contact in contacts:

            on_twitter = True if contact.find("span", text="On Twitter") else False

            if on_twitter:
                email_row = contact.find_all("tr", class_="contacts-field")[-1]
                email = email_row.find_all("span", class_="u-hiddenVisually")[-1]

                tw_running_emails.add(email.text.strip())

        count = 0

        with open(records_path, "r") as rf:
            with open(tw_running_records_path, 'w') as wf:

                for line in rf:
                    tokens = list(map(lambda x: x.strip(), line.split("\t")))
                    email = tokens[-1].lower()

                    if email in tw_running_emails:
                        count += 1

                        index = tokens[0]
                        fname = tokens[1]
                        mname = tokens[2]
                        lname = tokens[3]

                        flname = ' '.join(x for x in [fname, lname] if x)
                        tw_running_rec = '\t'.join([flname, email, fname, mname, lname, index])

                        wf.write(tw_running_rec + "\n")
        print(i, len(tw_running_emails), count)


if __name__ == "__main__":
    num_files = len(os.listdir(TW_IMPORTS_DIR))

    parse_contacts(0, num_files)
    parse_imports(0, num_files)

#    num_threads = 10
#    
#    for i in range(num_threads):
#        start = i * int(num_files / 10)
#        end = start + int((num_files / 10)) 
#        if i == num_threads - 1:
#            end = max(end, num_files)
#        
#        print(start, end)
#    
#        parse_con_thread = Thread(target = parse_contacts, name = 'pct_{}'.format(i), args = (start, end))
#        parse_imp_thread = Thread(target = parse_imports, name = 'pit_{}'.format(i), args = (start, end))
#        
#        parse_con_thread.start()
#        parse_imp_thread.start()
