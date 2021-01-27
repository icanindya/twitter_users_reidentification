from IPython.utils.syspathcontext import prepended_to_syspath
from nltk.util import ngrams
from collections import Counter
import math
import pandas as pd
import re
import textdistance
import sys
from Linkage.linkage_datasets_processors import preprocess_name

if len(sys.argv) > 1:

    LOCATION_TYPE = sys.argv[1]

    NAME_TYPE = sys.argv[2]

    ATTRIBUTE_TYPE = sys.argv[3]

    BIRTHDAY_TYPE = sys.argv[4]

    LINKAGE_TYPE = sys.argv[5]

    print(LOCATION_TYPE, NAME_TYPE, ATTRIBUTE_TYPE, BIRTHDAY_TYPE, LINKAGE_TYPE)

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside.csv'
NAME_MAPPING_PATH = r'D:\Data\Linkage\FL\FL18\name_processing\name_mapping.txt'
LOC_VOTERS_PATH = r'D:\Data\Linkage\FL\FL18\linkage\{}wise\voterside_{}.csv'

hypocorism_dict = {}

with open(NAME_MAPPING_PATH, 'r', encoding='utf-8') as rf:
    for line in rf:
        tokens = line.strip().split(',')
        short = tokens[0]
        hypocorism_dict[short] = tokens

def cosine_similarity_ngrams(text1, text2, n_start, n_end):

    ngrams1 = []
    ngrams2 = []

    for n in range(n_start, n_end + 1):
        ngrams1.extend([''.join(ngram) for ngram in ngrams(text1, n)])
        ngrams2.extend([''.join(ngram) for ngram in ngrams(text2, n)])

    vec1 = Counter(ngrams1)
    vec2 = Counter(ngrams2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def get_token(name, position):

    tokens = name.split()

    if position == 0 and len(tokens) > 0:

        return tokens[0]

    elif position == -1 and len(tokens) > 1:

        return tokens[-1]

    return ''

def count_parts_matched(voter_full_name, twitter_name):

    voter_name_parts_set = set()

    for token in voter_full_name.split():

        if token:

            voter_name_parts_set.add(token)

    twitter_name_parts_set = set()

    for token in twitter_name.split():

        if token:
            twitter_name_parts_set.update(hypocorism_dict.get(token, [token]))

    count = voter_name_parts_set.intersection(twitter_name_parts_set)

    return count


def count_parts_matched(voter_full_name, twitter_name):

    voter_name_parts_set = set()

    for token in voter_full_name.split():

        if token:
            voter_name_parts_set.add(token)

    twitter_name_parts_set = set()

    for token in twitter_name.split():

        if token:
            twitter_name_parts_set.update(hypocorism_dict.get(token, [token]))

    count = len(voter_name_parts_set.intersection(twitter_name_parts_set))

    return count

def count_prefix_matched(voter_full_name, twitter_name):

    voter_name_prefix_set = set()

    for token in voter_full_name.split():

        if len(token) >= 3:

            voter_name_prefix_set.add(token[:3])

    twitter_name_prefix_set = set()

    for token in twitter_name.split():

        if len(token) >= 3:

            twitter_name_prefix_set.add(token[:3])

    count = len(voter_name_prefix_set.intersection(twitter_name_prefix_set))

    return count

locations = pd.read_csv(LINKAGE_VOTER_PATH,
                        header=0,
                        usecols=[LOCATION_TYPE],
                        converters={LOCATION_TYPE: str})[LOCATION_TYPE].unique()

locations = [loc for loc in locations if loc.isalnum()]

df_loc_voters = {}


for loc in locations:
    voters = pd.read_csv(LOC_VOTERS_PATH.format(LOCATION_TYPE, loc), header=0, index_col=0, converters={'fname': str,
                                                                                           'mname': str,
                                                                                           'lname': str,
                                                                                         LOCATION_TYPE: str})
    voters['birthday'] = voters['dob'].apply(lambda x: x[:5])
    voters['fl_name'] = voters[['fname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
    voters['full_name'] = voters[['fname', 'mname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
    df_loc_voters[loc] = voters

df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH,
                         header=0,
                         converters={'twitter_name': str,
                                     'orig_' + LOCATION_TYPE: str,
                                     'orig_fname': str,
                                     'orig_mname': str,
                                     'orig_lname': str})
df_twitter['orig_fl_name'] = df_twitter[['orig_fname', 'orig_lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
df_twitter['orig_full_name'] = df_twitter[['orig_fname', 'orig_mname', 'orig_lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)


hit = miss = 0

for i, row in df_twitter.iterrows():

    voter_serial = row['voter_serial']
    twitter_name = row['twitter_name'] if NAME_TYPE == 'twitter' else ' '.join(row['orig_fl_name'].split())
    twitter_loc = row['orig_' + LOCATION_TYPE]
    twitter_birthday = row['orig_dob'][:5]
    pred_sex = row['pred_sex'] if ATTRIBUTE_TYPE == 'predicted' else row['orig_sex']
    pred_gen = row['pred_gen'] if ATTRIBUTE_TYPE == 'predicted' else row['orig_gen']
    pred_race = row['pred_race'] if ATTRIBUTE_TYPE == 'predicted' else row['orig_race']
    pred_party = row['pred_party'] if ATTRIBUTE_TYPE == 'predicted' else row['orig_party']

    fl_match = -1
    parts_match = -1
    prefix_match = -1
    sim_match = -1

    df_voter = df_loc_voters[twitter_loc]

    if BIRTHDAY_TYPE == 'include':

        df_voter = df_voter.loc[df_voter['birthday'] == twitter_birthday]

    twitter_name_tokens = [token.strip() for token in twitter_name.split()]
    twitter_fname = get_token(twitter_name, 0)
    twitter_lname = get_token(twitter_name, -1)
    twitter_fnames = hypocorism_dict.get(twitter_fname, [twitter_fname])

    df_voter_matched = df_voter.loc[(df_voter['fname'].isin(twitter_fnames)) &
                                    (df_voter['lname'] == twitter_lname)]

    fl_match = len(df_voter_matched)

    if len(df_voter_matched) == 0:

        twitter_name_parts_set = set()

        for token in twitter_name.split():
            twitter_name_parts_set.update(hypocorism_dict.get(token, [token]))

        twitter_name_parts = list(twitter_name_parts_set)

        df_voter_matched = df_voter.loc[(df_voter['fname'].isin(twitter_name_parts)) |
                                        (df_voter['mname'].isin(twitter_name_parts)) |
                                        (df_voter['lname'].isin(twitter_name_parts))]

    if len(df_voter_matched) == 0:

         status = 'none'

    elif len(df_voter_matched) >= 1:

        if 'name_sim' not in df_voter_matched.columns:

            df_voter_matched['name_sim'] = df_voter_matched['fl_name'].apply(textdistance.levenshtein.similarity, args=(twitter_name,))

        max_sim = df_voter_matched['name_sim'].max()
        df_voter_matched = df_voter_matched.loc[df_voter_matched['name_sim'] == max_sim]
        sim_match = len(df_voter_matched)

        if LINKAGE_TYPE == 'full':

            attribute_values = [('sex', pred_sex), ('race', pred_race), ('gen', pred_gen), ('party', pred_party)]

            for attribute, value in attribute_values:

                df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched[attribute] == value]

                if len(df_voter_matched_filtered) > 0:

                    df_voter_matched = df_voter_matched_filtered

        pred_voter_serial = df_voter_matched['name_sim'].idxmax()

        if voter_serial == pred_voter_serial:

            status = 'hit'
            hit += 1

        else:
            status = 'miss'
            miss += 1

    print('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(i + 1, hit, miss, (i + 1 - hit - miss), status, twitter_name, row['orig_full_name'], fl_match, parts_match, prefix_match, sim_match))

print(LOCATION_TYPE, NAME_TYPE, ATTRIBUTE_TYPE, BIRTHDAY_TYPE, LINKAGE_TYPE)






