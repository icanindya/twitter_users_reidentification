import re

import pandas as pd
import unidecode

import helper

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
TWITTER_NAME_HANDLE_PATH = r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_twitter_name_handle.csv"
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
RCAE_RES_PATH = r"D:\Data\Linkage\FL\FL18\attributes\predictions\race_nn_doc2vec.csv"


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

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    return name


twitter_ids_df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id'])
twitter_name_df = pd.read_csv(TWITTER_NAME_HANDLE_PATH, header=0, usecols=['twitter_name'],
                              converters={'twitter_name': str})
twitter_name_df['twitter_name'] = twitter_name_df['twitter_name'].apply(preprocess_name)

id_name_df = pd.concat([twitter_ids_df, twitter_name_df], axis=1)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_id'].tolist()

id_name_df = id_name_df.loc[id_name_df['twitter_id'].isin(test_ids)]

name_df = id_name_df[['twitter_name']]

name_df.reset_index(drop=True, inplace=True)

print(name_df.shape)

census_df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\surnames\Names_2010Census_processed.csv", header=0, converters={'name': str})

lname_prob_dict = {}

for i, row in census_df.iterrows():
    lname = row['name'].lower()

    prob_wh = row['pctwhite']/100
    prob_bl = row['pctblack']/100
    prob_ap = row['pctapi']/100
    prob_ia = row['pctaian']/100
    prob_mu = row['pct2prace']/100
    prob_hi = row['pcthispanic']/100

    lname_prob_dict[lname] = {'WH': prob_wh,
                              'BL': prob_bl,
                              'AP': prob_ap,
                              'IA': prob_ia,
                              'MU': prob_mu,
                              'HI': prob_hi,
                              'OT': 0.0,
                              'UN': 0.0
                              }

race_res_df = pd.read_csv(RCAE_RES_PATH, header=0)

print(race_res_df.shape)

df = pd.concat([name_df, race_res_df], axis=1)

thres = 0.72

count = 0

gamma = 1.25

for i, row in df.iterrows():

    orig_race = row['orig_race']
    pred_race = row['pred_race']
    pred_confidence = row[pred_race]

    pred_confidences = {'WH': row['WH'],
                        'BL': row['BL'],
                        'AP': row['AP'],
                        'IA': row['IA'],
                        'MU': row['MU'],
                        'HI': row['HI'],
                        'OT': row['OT'],
                        'UN': row['UN']
                        }



    twitter_name = row['twitter_name']

    name_parts = twitter_name.split()

    surname_confidences = {'WH': 0.0,
                           'BL': 0.0,
                           'AP': 0.0,
                           'IA': 0.0,
                           'MU': 0.0,
                           'HI': 0.0,
                           'OT': 0.0,
                           'UN': 0.0
                           }

    for part in name_parts[::-1]:

        if part in lname_prob_dict:

            surname_confidences = lname_prob_dict[part]

            print(part)

            break

    if max(surname_confidences, key=surname_confidences.get) == 'HI':

        pred_race = 'HI'

    elif pred_confidence < thres:

        avg_confidences = {}


        for key in pred_confidences:

            avg_confidences[key] = (pred_confidences[key] + surname_confidences[key])/2

        pred_race = max(avg_confidences, key=avg_confidences.get)

    if pred_race == orig_race:

        count += 1

        print(count, row['twitter_name'])

print(count/len(df))
