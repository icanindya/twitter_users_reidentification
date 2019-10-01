'''
Splits the records of FL_EXT_PATH files into NUM_SPLITS = 2000
files such that records having similar names are placed into 
different files. Records are sorted based on first name and 
last name cobination and neighbors are placed into different 
files.

Creates contact lists for the generated files.
'''

import csv
import os

FL_EXT_PATH = r'D:\Data\Linkage\FL\FL18\20181015_VoterDetail_Ext'
FL_SPLITS_PATH = r'D:\Data\Linkage\FL\FL18\fl_rec_splits_new'
FL_CON_SPLITS_PATH = r'D:\Data\Linkage\FL\FL18\fl_con_splits_new'

SEP = '\t'
tuples = []
NUM_SPLITS = 2000
rec_wfs = []
con_wfs = []
con_writers = []

NAME_CSV_IDX = 0
FNAME_CSV_IDX = 1
MNAME_CSV_IDX = 2
LNAME_CSV_IDX = 3
ID_CSV_IDX = 8
EMAIL_TYPE_CSV_IDX = 29
EMAIL_CSV_IDX = 30
PHONE_TYPE_CSV_IDX = 31
PHONE_CSV_IDX = 32

fields = ['Name', 'Given Name', 'Additional Name', 'Family Name', 'Yomi Name', 'Given Name Yomi', \
          'Additional Name Yomi', 'Family Name Yomi', 'Name Prefix', 'Name Suffix', 'Initials', \
          'Nickname', 'Short Name', 'Maiden Name', 'Birthday', 'Gender', 'Location', 'Billing Information', \
          'Directory Server', 'Mileage', 'Occupation', 'Hobby', 'Sensitivity', 'Priority', 'Subject', 'Notes', \
          'Language', 'Photo', 'Group Membership', 'E-mail 1 - Type', 'E-mail 1 - Value', 'Phone 1 - Type', \
          'Phone 1 - Value', 'Phone 2 - Type', 'Phone 2 - Value', 'Address 1 - Type', \
          'Address 1 - Formatted', 'Address 1 - Street', 'Address 1 - City', 'Address 1 - PO Box', \
          'Address 1 - Region', 'Address 1 - Postal Code', 'Address 1 - Country', \
          'Address 1 - Extended Address', 'Website 1 - Type', 'Website 1 - Value']


def get_csv_fields(line):
    tokens = line.split(SEP)
    tokens = list(map(lambda x: x.strip(), tokens))

    tokens = line.split(SEP)
    tokens = list(map(lambda x: x.strip(), tokens))

    index = tokens[0].strip()
    fname = tokens[1].replace(',', ' ')
    mname = tokens[2].replace(',', ' ')
    lname = tokens[3].replace(',', ' ')

    email = tokens[-1]
    phone = tokens[-2]
    if phone:
        phone = '+1' + phone

    fields = [''] * 46
    names = [fname, mname, lname]
    fields[NAME_CSV_IDX] = ' '.join(x for x in names if x)
    fields[FNAME_CSV_IDX] = fname
    fields[MNAME_CSV_IDX] = mname
    fields[LNAME_CSV_IDX] = lname
    fields[ID_CSV_IDX] = index
    fields[EMAIL_TYPE_CSV_IDX] = '* Home'
    fields[EMAIL_CSV_IDX] = email
    fields[PHONE_TYPE_CSV_IDX] = 'Mobile'
    fields[PHONE_CSV_IDX] = ''

    return fields


for item in os.listdir(FL_EXT_PATH):
    item_path = os.path.join(FL_EXT_PATH, item)
    if os.path.isfile(item_path):
        with open(item_path, 'r') as rf:
            for line in rf:
                tokens = line.split(SEP)
                tokens = list(map(lambda x: x.strip(), tokens))

                email = tokens[-1]

                if email:
                    fname = tokens[1].replace(',', ' ')
                    lname = tokens[3].replace(',', ' ')

                    flname = (fname + ' ' + lname).strip().upper()

                    tuples.append((flname, line))

sorted_flnames = sorted(tuples, key=lambda x: x[0])

for i in range(NUM_SPLITS):
    rec_wf = open(FL_SPLITS_PATH + r'\rec_{}.txt'.format(i), 'w')
    rec_wfs.append(rec_wf)

    con_wf = open(FL_CON_SPLITS_PATH + r'\con_{}.csv'.format(i), 'w', newline='')
    con_wfs.append(con_wf)

    con_writer = csv.writer(con_wf)
    con_writers.append(con_writer)
    con_writer.writerow(fields)

for i, tup in enumerate(sorted_flnames):
    rec_wfs[i % NUM_SPLITS].write(tup[1])
    con_writers[i % NUM_SPLITS].writerow(get_csv_fields(tup[1]))

for i in range(NUM_SPLITS):
    rec_wfs[i].close()
    con_wfs[i].close()
