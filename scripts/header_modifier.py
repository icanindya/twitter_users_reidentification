import csv
import helper

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

CSV_HEADER = ['twitter_id', 'voter_serial', 'dob', 'age', 'sex', 'race',
              'zip', 'city', 'party', 'tweet_startdate', 'tweet_enddate',
              'num_tweets', 'num_hashtags', 'num_mentions', 'num_urls',
              'num_media', 'num_symbols', 'num_polls', 'text']

with open(YEARLY_TWEETS_PATH + '1', 'w', newline='', encoding='utf-8') as wf:
    csv_writer = csv.writer(wf, delimiter=',')
    csv_writer.writerow(CSV_HEADER)

    with open(YEARLY_TWEETS_PATH, 'r', encoding='utf-8') as rf:
        csv_reader = csv.reader(rf, delimiter=',')

        for i, row in enumerate(csv_reader):
            if i != 0:
                csv_writer.writerow(row)
