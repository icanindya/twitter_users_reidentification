from IPython.utils.syspathcontext import prepended_to_syspath
from nltk.util import ngrams
from collections import Counter
import math
import pandas as pd
import re
import textdistance
from Linkage.linkage_datasets_processors import preprocess_name

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside_processed.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside_processed.csv'
NAME_MAPPING_PATH = r'D:\Data\Linkage\FL\FL18\name_processing\name_mapping.txt'
CITY_VOTERS_PATH = r'D:\Data\Linkage\FL\FL18\linkage\citywise\voterside_processed_{}.csv'

print('pred_attr_after, fl_name, lev')

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

cities = pd.read_csv(LINKAGE_VOTER_PATH,
                     header=0,
                     usecols=['city'],
                     converters={'city': str})['city'].unique()

df_city_voters = {}

for city in cities:
    voters = pd.read_csv(CITY_VOTERS_PATH.format(city), header=0, index_col=0, converters={'fname': str,
                                                                                           'mname': str,
                                                                                           'lname': str,
                                                                                           'city': str})
    voters['birthday'] = voters['dob'].apply(lambda x: x[:5])
    voters['fl_name'] = voters[['fname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
    voters['full_name'] = voters[['fname', 'mname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
    df_city_voters[city] = voters

df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH,
                         header=0,
                         converters={'twitter_name': str,
                                     'orig_city': str,
                                     'orig_fname': str,
                                     'orig_mname': str,
                                     'orig_lname': str})
df_twitter['orig_fl_name'] = df_twitter[['orig_fname', 'orig_lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
df_twitter['orig_full_name'] = df_twitter[['orig_fname', 'orig_mname', 'orig_lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)


hit = miss = 0

for i, row in df_twitter.iterrows():

    voter_serial = row['voter_serial']
    twitter_name = ' '.join(row['orig_fl_name'].split()) #row['orig_fl_name']
    twitter_city = row['orig_city']
    twitter_birthday = row['orig_dob'][:5]
    pred_sex = row['orig_sex'] #row['pred_sex']
    pred_gen = row['orig_gen'] #row['pred_gen']
    pred_race = row['orig_race'] #row['pred_race']
    pred_party = row['orig_party'] #row['pred_party']

    fl_match = -1
    parts_match = -1
    prefix_match = -1
    sim_match = -1

    df_voter = df_city_voters[twitter_city]
    # df_voter = df_voter.loc[df_voter['birthday'] == twitter_birthday]

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

        # df_voter['parts_matched'] = df_voter['full_name'].apply(count_parts_matched, args=(twitter_name,))
        #
        # df_voter_matched = df_voter.loc[df_voter['parts_matched'] > 0]
        #
        # parts_match = len(df_voter_matched)

    # if len(df_voter_matched) == 0:
    #
    #     df_voter['prefix_matched'] = df_voter['full_name'].apply(count_prefix_matched, args=(twitter_name,))
    #
    #     df_voter_matched = df_voter.loc[df_voter['prefix_matched'] > 1]
    #
    #     prefix_match = len(df_voter_matched)

    attribute_values = [('sex', pred_sex), ('race', pred_race), ('gen', pred_gen), ('party', pred_party)]

    for attribute, value in attribute_values:

        df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched[attribute] == value]

        if len(df_voter_matched_filtered) > 0:

            df_voter_matched = df_voter_matched_filtered


    if len(df_voter_matched) == 0:

         status = 'none'

    elif len(df_voter_matched) >= 1:

        if 'name_sim' not in df_voter_matched.columns:

            df_voter_matched['name_sim'] = df_voter_matched['fl_name'].apply(textdistance.levenshtein.similarity, args=(twitter_name,))

        max_sim = df_voter_matched['name_sim'].max()
        df_voter_matched = df_voter_matched.loc[df_voter_matched['name_sim'] == max_sim]
        sim_match = len(df_voter_matched)

        pred_voter_serial = df_voter_matched['name_sim'].idxmax()

        if voter_serial == pred_voter_serial:

            status = 'hit'
            hit += 1

        else:
            status = 'miss'
            miss += 1

    print('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(i + 1, hit, miss, status, twitter_name, row['orig_full_name'], fl_match, parts_match, prefix_match, sim_match))








