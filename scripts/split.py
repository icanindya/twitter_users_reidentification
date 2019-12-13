import helper

tweet_tokenzier = helper.CustomTweetTokenizer(preserve_case=True, reduce_len=False,
                                              strip_handles=False, convert_urls=True)

path = r"D:\Data\Linkage\FL\FL18\all_tweets\network_tweets.txt"

with open(r"D:\Data\Linkage\FL\FL18\all_tweets\network_tweets_1.txt", 'w', encoding='utf-8') as wf:
    with open(path, 'r', encoding='utf-8') as rf:
        for i, line in enumerate(rf):
            line = line.rstrip()
            line = line.replace('\u001a', '')
            tokens = [x.lower() for x in tweet_tokenzier.tokenize(line) if not helper.stop_or_mention(x)]
            modified_line = ' '.join(tokens)
            wf.write('{}\n'.format(modified_line))

