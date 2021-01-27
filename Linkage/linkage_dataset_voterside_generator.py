import csv
import helper
import os
import unidecode
import re


def preprocess_name(name, title=False):

    # Remove parethesized content
    name = name.replace(r'\(.*\)', '')

    # Convert accented characters
    name = unidecode.unidecode(name)

    # Replace '-', '_' and '.' with ' ':
    name = name.replace('-', ' ').replace('_', ' ').replace('.', ' ')

    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)

    # Make lower-case
    name = name.lower()

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    # Optionally titlecase
    if title:

        name = name.title()

    return name


def preprocess_city(city):

    city = re.sub(r'\W+', '', city)
    city = city.lower()
    return city

FL_EXT_PATH = r'D:\Data\Linkage\FL\FL18\20181015_VoterDetail_Ext'
LINKAGE_DSB = r'D:\Data\Linkage\FL\FL18\linkage\voterside.csv'

fieldnames = ['voter_serial',
              'fname',
              'mname',
              'lname',
              'name',
              'sex',
              'race',
              'dob',
              'gen',
              'party',
              'city',
              'county',
              'zip']

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
                city = tokens[9].upper()
                zip = tokens[10][:5]
                county = tokens[11].upper()
                phone = tokens[13]
                email = tokens[14].strip()
                gen = helper.get_generation(dob)

                fname = preprocess_name(fname, False)
                mname = preprocess_name(mname, False)
                lname = preprocess_name(lname, False)
                name = ' '.join([x for x in [fname, mname, lname]])

                city = preprocess_city(city)

                writer.writerow([voter_serial,
                                 fname,
                                 mname,
                                 lname,
                                 name,
                                 sex,
                                 race,
                                 dob,
                                 gen,
                                 party,
                                 city,
                                 county,
                                 zip])


