import csv
import helper

SINGLE_TWEET_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\single_tweet_tokens.csv'
CSV_HEADER = 'tokens_joined'

mongo_client = helper.get_mongo_client()
tweet_tokenizer = helper.CustomTweetTokenizer(preserve_case=True, reduce_len=False,
                                              strip_handles=False, convert_urls=True)

twitter_db = mongo_client['twitter']
tweets_col = twitter_db['tweets']
voters_col = twitter_db['voters']
ground_truths_col = twitter_db['ground_truths']

tweet_objs = tweets_col.find({'retweeted_status': {'$exists': False}})

tuples = [(x['twitter_id'], x['voter_serial']) for x in ground_truths_col.find({})]

count = 0

with open(SINGLE_TWEET_TOKENS_PATH, 'w', newline='', encoding='utf-8') as wf_csv:
    writer = csv.writer(wf_csv, delimiter=',')
    writer.writerow([CSV_HEADER])

    for twitter_id, voter_serial in tuples:

        tweet_objs = tweets_col.find({'user.id_str': twitter_id, 'retweeted_status': {'$exists': False}})
        tweets = [tweet_obj['text'].replace('\0', '') for tweet_obj in tweet_objs]

        for tweet in tweets:
            tokens = tweet_tokenizer.tokenize(tweet)
            tokens_joined = ' '.join(tokens)
            writer.writerow([tokens_joined])

            count += 1
            if count % 1000 == 0:
                print('processed {} tweets'.format(count))
                wf_csv.flush()

print('proceessed total {} tweets'.format(count))
