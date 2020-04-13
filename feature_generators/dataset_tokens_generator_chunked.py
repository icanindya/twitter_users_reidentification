import pandas as pd
import csv
import sys
import os

from docutils.nodes import header

import helper
import pandas as pd

ALL_TWEETS_CHUNKED_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_chunked.csv'
HEADER = ['tokens25_joined', 'tokens50_joined', 'tokens75_joined', 'tokens100_joined', 'tokens125_joined', 'tokensbeyond_joined']

def generate_tokens(dataset_path, tokens_path):

    tweet_tokenzier = helper.CustomTweetTokenizer(preserve_case=False, reduce_len=False,
                                                  strip_handles=True, convert_urls=True)

    with open(tokens_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(HEADER)

        with open(dataset_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)

                tokens25 = tweet_tokenzier.tokenize(row['text25'])
                tokens50 = tweet_tokenzier.tokenize(row['text50'])
                tokens75 = tweet_tokenzier.tokenize(row['text75'])
                tokens100 = tweet_tokenzier.tokenize(row['text100'])
                tokens125 = tweet_tokenzier.tokenize(row['text125'])
                tokensbeyond = tweet_tokenzier.tokenize(row['text125'])

                tokens25_joined = ' '.join(tokens25)
                tokens50_joined = ' '.join(tokens50)
                tokens75_joined = ' '.join(tokens75)
                tokens100_joined = ' '.join(tokens100)
                tokens125_joined = ' '.join(tokens125)
                tokensbeyond_joined = ' '.join(tokensbeyond)

                csv_writer.writerow([tokens25_joined, tokens50_joined,
                                     tokens75_joined,tokens100_joined,
                                     tokens125_joined, tokensbeyond_joined])

dataset_path = ALL_TWEETS_CHUNKED_PATH
file_name, file_ext = os.path.splitext(dataset_path)
tokens_path = file_name + '_tokens.csv'

generate_tokens(dataset_path, tokens_path)



