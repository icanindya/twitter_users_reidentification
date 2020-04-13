from nltk.util import ngrams
from collections import Counter
import math
import pandas as pd

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside_processed.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside_processed.csv'
NAME_MAPPING_PATH = r'D:\Data\Linkage\FL\FL18\name_processing\name_mapping.txt'
CITY_VOTERS_PATH = r'D:\Data\Linkage\FL\FL18\linkage\citywise\voterside_processed_{}.csv'

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


name_dict = {}

with open(NAME_MAPPING_PATH, 'r', encoding='utf-8') as rf:
    for line in rf:
        tokens = line.split(',')
        short = tokens[0]
        name_dict[short] = tokens

cities = pd.read_csv(LINKAGE_VOTER_PATH,
                     header=0,
                     usecols=['city'],
                     converters={'city': str})['city'].unique()

df_city_voter = {}

for city in cities:
    city = city.strip().replace('/', '+')
    if city not in ['', '*']:
        df_city_voter[city] = pd.read_csv(CITY_VOTERS_PATH.format(city), header=0, index_col=0)


df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH,
                         header=0,
                         converters={'twitter_name': str,
                                     'orig_city': str,
                                     'orig_fname': str,
                                     'orig_mname': str,
                                     'orig_lname': str})

hit = miss = 0

for i, row in df_twitter.iterrows():

    voter_serial = row['voter_serial']
    twitter_name = row['twitter_name']
    twitter_city = row['orig_city']
    pred_sex = row['pred_sex']
    pred_gen = row['pred_gen']
    pred_race = row['pred_race']
    pred_party = row['pred_party']
    orig_fname = row['orig_fname']
    orig_mname = row['orig_mname']
    orig_lname = row['orig_lname']
    orig_names = [orig_fname, orig_mname, orig_lname]

    orig_name = ' '.join([n for n in orig_names if n]).lower()

    twitter_city = twitter_city.strip().replace('/', '+')
    df_voter = df_city_voter[twitter_city]

    twitter_name_tokens = [token.strip() for token in twitter_name.split()]

    if len(twitter_name_tokens) >= 2:

        twitter_fname = twitter_name_tokens[0]
        twitter_lname = twitter_name_tokens[-1]

        if twitter_fname in name_dict:
            twitter_fnames = name_dict[twitter_fname]
        else:
            twitter_fnames = [twitter_fname]

        df_voter_matched = df_voter.loc[(df_voter['fname'].isin(twitter_fnames)) &
                                        (df_voter['lname'] == twitter_lname)]

        if len(df_voter_matched) == 0:
            df_voter_matched = df_voter.loc[(df_voter['fname'].isin(twitter_fnames)) |
                                             (df_voter['lname'] == twitter_fname) |
                                             (df_voter['fname'] == twitter_lname) |
                                             (df_voter['lname'] == twitter_lname)]

    elif len(twitter_name_tokens) == 1:

        if twitter_name in name_dict:
            twitter_names = name_dict[twitter_name]
        else:
            twitter_names = [twitter_name]
        df_voter_matched = df_voter.loc[(df_voter['fname'].isin(twitter_names)) |
                                        (df_voter['lname'].isin(twitter_names))]


    attribute = 0

    while len(df_voter_matched) > 1 and attribute < 4:

        if attribute == 0:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched['sex'] == pred_sex]
        elif attribute == 1:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched['gen'] == pred_gen]
        elif attribute == 2:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched['race'] == pred_race]
        elif attribute == 3:
            df_voter_matched_filtered = df_voter_matched.loc[df_voter_matched['party'] == pred_party]

        attribute += 1

        if len(df_voter_matched_filtered) > 0:

            df_voter_matched = df_voter_matched_filtered

    if len(df_voter_matched) == 0:

         status = 'none'

    elif len(df_voter_matched) >= 1:

        df_voter_matched['name_sim'] = df_voter_matched['full_name'].apply(cosine_similarity_ngrams, args=(twitter_name, 2, 4))
        pred_voter_serial = df_voter_matched['name_sim'].idxmax()

        if voter_serial == pred_voter_serial:

            status = 'hit'
            hit += 1

        else:
            status = 'miss'
            miss += 1

    print('{}, {}, {}, {}, {}, {}'.format(i + 1, hit, miss, status, twitter_name, orig_name, len(df_voter_matched)))








