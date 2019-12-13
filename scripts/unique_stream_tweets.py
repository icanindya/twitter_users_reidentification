GEO_STREAM_PATH = r"D:\Data\Linkage\FL\FL18\all_tweets\stream_geo.txt"
LANG_STREAM_PATH = r"D:\Data\Linkage\FL\FL18\all_tweets\stream_lang.txt"

tweet_ids = []

with open(GEO_STREAM_PATH, 'r', encoding='utf-8') as rf:
    for line in rf:
        user_tweet_id = line[:line.find(',')]
        tweet_id = user_tweet_id.split('-')[1]
        tweet_ids.append(tweet_id)

with open(LANG_STREAM_PATH, 'r', encoding='utf-8') as rf:
    for line in rf:
        user_tweet_id = line[:line.find(',')]
        tweet_id = user_tweet_id.split('-')[1]
        tweet_ids.append(tweet_id)

print(len(tweet_ids))
print(len(set(tweet_ids)))