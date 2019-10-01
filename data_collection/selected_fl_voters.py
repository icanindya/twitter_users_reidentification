import os

import mongo_client as mc

'''
Stores the voter records from FL_REC_SPLITS_DIR as
JSON objects into MongoDB.
'''

FL_REC_SPLITS_DIR = r'D:\Data\Linkage\FL\FL18\fl_rec_splits'


def store_voters(mongo_client, voter_objs):
    twitter_db = mongo_client['twitter']
    main_col = twitter_db['voters']
    main_col.insert_many(voter_objs)


if __name__ == '__main__':

    voter_objs = []

    for i in range(2000):
        voter_file_path = os.path.join(FL_REC_SPLITS_DIR, 'rec_{}.txt'.format(i))

        with open(voter_file_path, 'r') as rf:
            for line in rf:
                tokens = list(map(lambda x: x.strip(), line.split('\t')))
                voter_obj = {'serial': tokens[0],
                             'fname': tokens[1],
                             'mname': tokens[2],
                             'lname': tokens[3],
                             'sex': tokens[4],
                             'dob': tokens[5],
                             'race_code': tokens[6],
                             'add1': tokens[7],
                             'add2': tokens[8],
                             'city': tokens[9],
                             'zip_code': tokens[10],
                             'county_code': tokens[11],
                             'party': tokens[12],
                             'phone': tokens[13],
                             'email': tokens[14]
                             }
                voter_objs.append(voter_obj)

    store_voters(mc.get(), voter_objs)
