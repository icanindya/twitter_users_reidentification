import csv
import helper
import unicodedata
import os

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'

STREAM_LANG_TWEETS_PATH = r"D:\Data\Linkage\FL\FL18\all_tweets\stream_lang.txt"
STREAM_GEO_TWEETS_PATH = r"D:\Data\Linkage\FL\FL18\all_tweets\stream_geo.txt"
TRAINER_TWEET_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\trainer_tweet_tokens.csv'
CSV_HEADER = 'tokens_joined'

mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
tweets_col = twitter_db['tweets']

tweet_id_set = set()



USE_STREAMS = False


def preprocess(text):

    text = ''.join(c for c in text if unicodedata.category(c).startswith(('C', )) is False)
    text = ''.join(' ' if unicodedata.category(c).startswith(('Zl', 'Zp')) else c for c in text)
    tokenizer = helper.CustomTweetTokenizer(preserve_case=False, reduce_len=False, strip_handles=True, convert_urls=True)
    tokens = tokenizer.tokenize(text)
    return ' '.join(tokens)


def generate_ftext_train_input():

    dataset_path = ALL_TWEETS_PATH
    file_name, file_ext = os.path.splitext(dataset_path)
    model_tokens_path = file_name + '_tokens.csv'
    fb_ftext_input_path = file_name + '_fb_ftext_input.txt'
    with open(fb_ftext_input_path, 'w', encoding='utf-8') as wf:
        with open(model_tokens_path, 'r', encoding='utf-8') as rf:
            csv_reader = csv.DictReader(rf, delimiter=',')
            for i, row in enumerate(csv_reader):
                if i % 100 == 0:
                    print('write csv row', i)
                # assume there's one document per line, tokens separated by whitespace
                line = preprocess(row['tokens_joined'])
                wf.write('{}\n'.format(line))


def gen_embed_train_dataset():

    count = 0

    with open(TRAINER_TWEET_TOKENS_PATH, 'w', encoding='utf-8') as wf:

        wf.write('tokens_joined\n')

        for tweet_obj in tweets_col.find({}):

            tweet_id = tweet_obj['id_str']

            if tweet_id not in tweet_id_set:

                text = preprocess(tweet_obj['text'])

                wf.write('{}\n'.format(text))

                tweet_id_set.add(tweet_id)

                count += 1

                if count % 1000 == 0:
                    print(count)

        if USE_STREAMS:

            stream_paths = [STREAM_LANG_TWEETS_PATH, STREAM_GEO_TWEETS_PATH]

            for stream_path in stream_paths:

                with open(stream_path, 'r', encoding='utf-8') as rf:

                    for line in rf:
                        sep_index = line.find(',')
                        user_tweet_id = line[:sep_index]
                        tweet_text = line[sep_index + 2:].rstrip()
                        tweet_id = user_tweet_id.split('-')[1]

                        if tweet_id not in tweet_id_set:
                            text = preprocess(tweet_text)

                            wf.write('{}\n'.format(text))

                            tweet_id_set.add(tweet_id)

                            count += 1

                            if count % 1000 == 0:
                                print(count)

        print(count)

generate_ftext_train_input()