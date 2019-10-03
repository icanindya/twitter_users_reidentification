import os

import helper

TW_RUNNING_REC_DIR = r'D:\Data\Linkage\FL\FL18\tw_running_records_new'
MASTER_GROUND_TRUTHS_DIR = r'D:\Data\Linkage\FL\FL18\master_ground_truths'


def store_ground_truths(mongo_client, ground_truth_objs):
    twitter_db = mongo_client['twitter']
    main_col = twitter_db['ground_truths']
    main_col.insert_many(ground_truth_objs)


if __name__ == '__main__':

    ground_truth_objs = []

    count = 0

    for i in range(2000):

        tw_running_rec_file = os.path.join(TW_RUNNING_REC_DIR, 'tw_running_rec_{}.txt'.format(i))
        master_ground_truths_file = os.path.join(MASTER_GROUND_TRUTHS_DIR, 'master_ground_truths_{}.txt'.format(i))

        flnames = []
        serials = []

        with open(tw_running_rec_file, 'r') as rf_voters:
            for line in rf_voters:
                tokens = list(map(lambda x: x.strip(), line.split('\t')))
                serial = tokens[-1]
                flname = tokens[0]
                serials.append(serial)
                flnames.append(flname)

        vt_indexes_visited = {}

        with open(master_ground_truths_file, 'r') as rf_accounts:
            for index, line in enumerate(rf_accounts):
                vt_index = int(line[:line.index(':\t')]) - 1

                if vt_index in vt_indexes_visited:
                    raise Exception('Already visited index {} at file {}'.format(vt_index, i))

                vt_indexes_visited[vt_index] = 1

                twitter_info = line[line.index(':\t') + 2:]

                attributes = twitter_info.split('\t')

                if len(attributes) > 3:
                    twitter_name = attributes[0]
                    twitter_id = attributes[2]

                    count += 1

                    print('{} : {}  -----  {}'.format(count, twitter_name, flnames[index]))

                    ground_truth_obj = {'twitter_id': twitter_id, 'voter_serial': serials[vt_index]}

                    ground_truth_objs.append(ground_truth_obj)

    #                    if twitter_name == '':
    #                        print(master_ground_truths_file, index)

    store_ground_truths(helper.get_mongo_client(), ground_truth_objs)
