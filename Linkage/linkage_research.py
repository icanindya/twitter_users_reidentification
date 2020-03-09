import pandas as pd
import unidecode
import re

def preprocess_name(name):

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

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    return name


name = 'Ms.Rach Marry-Foxx(*_*) '

print(preprocess_name(name))

exit(0)

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv'
NAME_MAPPING_PATH = r'D:\Data\Linkage\FL\FL18\name_processing\name_mapping.txt'

name_dict = {}
with open(NAME_MAPPING_PATH, 'r', encoding='utf-8') as rf:
    for line in rf:
        tokens = line.split(',')
        short = tokens[0]
        name_dict[short] = tokens

df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH, header=0, converters={'twitter_name': str,
                                                                     'twitter_handle': str,
                                                                     'orig_fname': str,
                                                                     'orig_mname': str,
                                                                     'orig_lname': str})

df_voter = pd.read_csv(LINKAGE_VOTER_PATH, header=0,  converters={'fname': str, 'mname': str,
                                                                  'lname': str, 'sex': str,
                                                                  'race': str, 'dob': str,
                                                                  'party': str, 'city': str})

# Only keep voters born after 1945

df_voter['yob'] = df_voter['dob'].apply(lambda x: int(x[-4:]))
df_voter = df_voter.loc[df_voter['yob'] > 1945]

#

df_voter['fname'] = df_voter['fname'].apply(lambda x: x.lower())
df_voter['mname'] = df_voter['mname'].apply(lambda x: x.lower())
df_voter['lname'] = df_voter['lname'].apply(lambda x: x.lower())

df_voter.set_index('voter_serial', drop=False, inplace=True)


for i, row in df_twitter.iterrows():

    voter_serial = row['voter_serial']
    twitter_city = row['orig_city']
    original_name_parts = [row['orig_fname'], row['orig_mname'], row['orig_lname']]
    original_name = ' '.join([part for part in original_name_parts if part != '']).lower()

    twitter_name = unidecode.unidecode(row['twitter_name']).lower()
    twitter_name_tokens = [token.strip() for token in twitter_name.split()]

    pred_sex = row['pred_sex']
    pred_gen = row['pred_gen']
    pred_race = row['pred_race']
    pred_party = row['pred_party']

    if len(twitter_name_tokens) == 1:
        twitter_fname = twitter_name_tokens[0]

        if twitter_fname in name_dict:
            twitter_fnames = name_dict[twitter_fname]
        else:
            twitter_fnames = [twitter_fname]

        df_voter_matched = df_voter.loc[(df_voter['city'] == twitter_city) &
                                        (df_voter['fname'].isin(twitter_fnames))]

    elif len(twitter_name_tokens) == 2:
        twitter_fname = twitter_name_tokens[0]
        twitter_lname = twitter_name_tokens[1]

        if twitter_fname in name_dict:
            twitter_fnames = name_dict[twitter_fname]
        else:
            twitter_fnames = [twitter_fname]

        df_voter_matched = df_voter.loc[(df_voter['city'] == twitter_city) &
                                        (df_voter['fname'].isin(twitter_fnames)) &
                                        (df_voter['lname'] == twitter_lname)]

    attribute = 0

    while len(df_voter_matched) > 1 and attribute < 4:

        if attribute == 0:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter['sex'] == pred_sex]
        elif attribute == 1:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter['gen'] == pred_gen]
        elif attribute == 2:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter['race'] == pred_race]
        elif attribute == 3:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter['party'] == pred_party]

        attribute += 1

        if len(df_voter_matched_filtered) > 0:

            df_voter_matched = df_voter_matched_filtered


    if len(df_voter_matched > 0):

        pass



    else:
        continue

    print('{} | {}, found: {}, matchable: {}'.format(twitter_name, original_name, len(df_voter_matched), voter_serial in df_voter_matched.index))








