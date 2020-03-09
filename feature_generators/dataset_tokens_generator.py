import pandas as pd
import csv
import sys
import os
import helper

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'


def generate_tokens(dataset_path, tokens_path):

    tweet_tokenzier = helper.CustomTweetTokenizer(preserve_case=False, reduce_len=False,
                                                  strip_handles=True, convert_urls=True)

    with open(tokens_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        csv_writer.writerow(['tokens_joined'])

        with open(dataset_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')

            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)

                tokens = tweet_tokenzier.tokenize(row['text'])
                tokens_joined = ' '.join(tokens)
                csv_writer.writerow([tokens_joined])


option = sys.argv[1]

if option == '1':
    dataset_path = ALL_TWEETS_PATH
elif option == '2':
    dataset_path = YEARLY_TWEETS_PATH

file_name, file_ext = os.path.splitext(dataset_path)
tokens_path = file_name + '_tokens.csv'

generate_tokens(dataset_path, tokens_path)




