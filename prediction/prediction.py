import csv
import sys

from text_processing import FeatureExtractor

maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)

DS_ALL_TWEETS_PER_YEAR_PATH = r'D:\Data\Linkage\FL\FL18\tweets\ds_all_tweets_per_year.csv'
DS_ALL_TWEETS_PER_YEAR_FEATURES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\ds_all_tweets_per_year_features.csv'

with open(DS_ALL_TWEETS_PER_YEAR_PATH, 'r', newline='', encoding='utf-8') as rf_csv:
    csv_reader = csv.reader(rf_csv, delimiter=',')

    with open(DS_ALL_TWEETS_PER_YEAR_FEATURES_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        for read_row in csv_reader:
            twitter_id = read_row[0]
            combined_tweets = read_row[1]
            num_tweets = int(read_row[2])
            num_hashtags = int(read_row[3])
            num_mentions = int(read_row[4])
            num_urls = int(read_row[5])
            num_media = int(read_row[6])
            num_symbols = int(read_row[7])
            num_polls = int(read_row[8])

            age = int(read_row[9])
            sex = read_row[10]
            race_code = read_row[11]
            zip_code = read_row[12]
            city = read_row[13]
            party = read_row[14]

            attributes = [age, sex, race_code, zip_code, city, party]

            fe = FeatureExtractor(text=combined_tweets, num_tweets=num_tweets, num_hashtags=num_hashtags,
                                  num_mentions=num_mentions, num_urls=num_urls, num_media=num_media,
                                  num_symbols=num_symbols, num_polls=num_polls)

            features = [str(f) for f in fe.get_all_features()]

            write_row = [twitter_id] + features + attributes
            #            print(write_row)
            writer.writerow(write_row)
