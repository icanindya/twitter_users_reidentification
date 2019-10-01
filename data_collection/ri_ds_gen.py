'''
Dataset: RI voter records 2018 snapshot.
Indexifies the records in FL_BASE_PATH files.
Shrink individual records by extracting only the required attributes.
Stores the indexed shrinked records in FL_EXT_PATH files. 
'''

import os
import re

from validate_email import validate_email

RI_BASE_PATH = r'D:\Data\Linkage\RI\RI18\'
RI_EXT_PATH = r'D:\Data\Linkage\RI\RI18\'
SEP = '\t'

phone_regex = re.compile(r'^\d{10}$')

count = 0
cnt_valid_phone_email = 0
cnt_valid_phone = 0
cnt_valid_email = 0

for item in os.listdir(RI_BASE_PATH):
    item_path = os.path.join(RI_BASE_PATH, item)
    if os.path.isfile(item_path):
        with open(item_path, 'r') as rf:

            with open(os.path.join(RI_EXT_PATH, item), 'w') as wf:

                for line in rf:

                    count += 1

                    tokens = line.split(SEP)
                    tokens = list(map(lambda x: x.strip(), tokens))

                    row_num = str(count)
                    fname = tokens[4]
                    mname = tokens[5]
                    lname = tokens[2]
                    add1 = tokens[7]
                    add2 = tokens[8]
                    city = tokens[9]
                    zipcode = tokens[11]
                    county_code = tokens[0]
                    gender = tokens[19]
                    race = tokens[20]
                    dob = tokens[21]
                    party = tokens[23]
                    phone = tokens[34] + tokens[35] + tokens[36]
                    email = tokens[37]

                    valid_phone = phone_regex.match(phone)
                    valid_email = validate_email(email)

                    if valid_phone and valid_email:
                        cnt_valid_phone_email += 1
                        cnt_valid_phone += 1
                        cnt_valid_email += 1
                    elif valid_phone:
                        cnt_valid_phone += 1
                        email = ''
                    elif valid_email:
                        cnt_valid_email += 1
                        phone = ''
                    else:
                        phone = ''
                        email = ''

                    attributes = [row_num, fname, mname, lname, gender, dob, race, add1, add2, city, zipcode,
                                  county_code, party, phone, email]

                    record_text = SEP.join(attributes)

                    wf.write(record_text + '\n')

print(count)
print(cnt_valid_phone_email)
print(cnt_valid_phone)
print(cnt_valid_email)
