import helper
import csv

DS_TWITTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside.csv"
DS_VOTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv"

pred_dict = {}

with open(DS_TWITTERSIDE_PATH, 'r', encoding='utf-8') as rf:
    csv_reader = csv.DictReader(rf, delimiter=',')
    for i, row in enumerate(csv_reader):
        pred_dob_tokens = row['pred_yob'].split('-')
        pred_dob_start = int(pred_dob_tokens[0])
        pred_dob_end = int(pred_dob_tokens[1])
        pred_dict[row['voter_serial']] = {'twitter_name': row['twitter_name'].lower(),
                                          'sex': row['pred_sex'],
                                          'race': row['pred_race'],
                                          'dob_start': pred_dob_start,
                                          'dob_end': pred_dob_end,
                                          'party': row['pred_party']}

num_names_matched = 0
num_fnames_matched = 0
num_flnames_matched = 0
num_fmlnames_matched = 0
num_attributes_matched = 0
num_names_attributes_matched = 0

with open(DS_VOTERSIDE_PATH, 'r', encoding='utf-8') as rf:
    csv_reader = csv.DictReader(rf, delimiter=',')
    for i, row in enumerate(csv_reader):
        if row['voter_serial'] in pred_dict:
            pred_dict_obj = pred_dict[row['voter_serial']]

            # name related matching
            names_matched = False

            fname = str(row['fname']).lower()
            flname = ' '.join([str(row['fname']), str(row['lname'])]).lower()
            fmlname = ' '.join([str(row['fname']), str(row['mname']), str(row['lname'])]).lower()

            if fname == pred_dict_obj['twitter_name']:
                names_matched = True
                num_names_matched += 1
                num_fnames_matched += 1
            elif flname == pred_dict_obj['twitter_name']:
                names_matched = True
                num_names_matched += 1
                num_flnames_matched += 1
            elif fmlname == pred_dict_obj['twitter_name']:
                names_matched = True
                num_names_matched += 1
                num_fmlnames_matched += 1

            # attribute related matching
            attributes_matched = False

            if row['sex'] == pred_dict_obj['sex'] and \
                    row['race'] == pred_dict_obj['race'] and \
                    pred_dict_obj['dob_start'] <= int(row['yob']) <= pred_dict_obj['dob_end'] and \
                    row['party'] == pred_dict_obj['party']:
                attributes_matched = True
                num_attributes_matched += 1

            if names_matched & attributes_matched:
                num_names_attributes_matched += 1

            print(num_names_matched, num_attributes_matched, num_names_attributes_matched)

print(num_names_matched)
print(num_fnames_matched)
print(num_flnames_matched)
print(num_fmlnames_matched)
print(num_attributes_matched)
print(num_names_attributes_matched)
print(len(pred_dict))