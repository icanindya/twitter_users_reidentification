import csv
import helper
import os

FL_EXT_PATH = r'D:\Data\Linkage\FL\FL18\20181015_VoterDetail_Ext'
LINKAGE_DSB = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv'

fieldnames = ['voter_serial', 'fname', 'mname', 'lname',
              'sex', 'race', 'dob', 'party', 'city']

with open(LINKAGE_DSB, 'w', newline='', encoding='utf-8') as wf_csv:
    writer = csv.writer(wf_csv, delimiter=',')
    writer.writerow(fieldnames)
    for filenname in os.listdir(FL_EXT_PATH):
        with open(os.path.join(FL_EXT_PATH, filenname), 'r') as rf:
            for line in rf:
                tokens = line.split('\t')
                voter_serial = tokens[0]
                fname = tokens[1]
                mname = tokens[2]
                lname = tokens[3]
                sex = tokens[4]
                race = helper.get_short_race(int(tokens[6]))
                dob = tokens[5] if tokens[5] else '00/00/0000'
                party = helper.get_short_party(tokens[12])
                city = tokens[9]
                zip = tokens[10]
                county = tokens[11]
                phone = tokens[13]
                email = tokens[14].strip()
                writer.writerow([voter_serial, fname, mname, lname,
                                 sex, race, dob, party, city])


