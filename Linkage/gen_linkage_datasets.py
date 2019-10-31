import csv
import helper
import os

FL_EXT_PATH = r'D:\Data\Linkage\FL\FL18\20181015_VoterDetail_Ext'
LINKAGE_DSB = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dsb_agegrouped.csv'

count = 0
fieldnames = ['index', 'fname', 'mname', 'lname', 'gender', 'yob', 'race',
              'add1', 'add2', 'city', 'zipcode', 'county_code', 'party',
              'phone', 'email']

with open(LINKAGE_DSB, 'w', newline='', encoding='utf-8') as wf_csv:
    writer = csv.writer(wf_csv, delimiter=',')
    writer.writerow(fieldnames)
    for filenname in os.listdir(FL_EXT_PATH):
        with open(os.path.join(FL_EXT_PATH, filenname), 'r') as rf:
            for line in rf:
                tokens = line.split('\t')
                index = str(count)
                fname = tokens[1]
                mname = tokens[2]
                lname = tokens[3]
                gender = tokens[4]
                if tokens[5]:
                    yob = helper.get_curr_age_label(tokens[5])
                else:
                    yob = '-'
                race = tokens[6]
                add1 = tokens[7]
                add2 = tokens[8]
                city = tokens[9]
                zipcode = tokens[10]
                county_code = tokens[11]
                party = tokens[12]
                phone = tokens[13]
                email = tokens[14].strip()
                writer.writerow([index, fname, mname, lname, gender, yob, race,
                                 add1, add2, city, zipcode, county_code, party,
                                 phone, email])
                count += 1

