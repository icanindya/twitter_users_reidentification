import helper

tweet_user_ids = set()
with open(r'D:\Data\Linkage\Other Datasets\Age\Zhang_ICWSM_2016\tweetsID.txt', 'r') as rf:
    for line in rf:
        if line.startswith('%'):
            tokens = line.strip().split(',')
            user_id = tokens[0].strip()[1:]
            # print(user_id)
            tweet_user_ids.add(user_id)

print(len(tweet_user_ids))
label_user_ids = set()
with open(r'D:\Data\Linkage\Other Datasets\Age\Zhang_ICWSM_2016\ageLabels.txt', 'r') as rf:
    for line in rf:
        tokens = line.strip().split(' ')
        user_id = tokens[0].strip()
        # print(user_id)
        label_user_ids.add(user_id)

print(len(label_user_ids))

common_user_ids = list(tweet_user_ids.intersection(label_user_ids))

mongo_client = helper.get_mongo_client()

maif_db = mongo_client['maif_db']
users_col = maif_db['users']
tweets_col = maif_db['tweets']

user_objs = users_col.find({'id_str': {'$in': common_user_ids}})

available_user_ids = {user_obj['id_str'] for user_obj in user_objs}

print(len(available_user_ids))

tweet_user_ids = set(tweets_col.distinct('user.id_str'))

available_notweet_user_ids = available_user_ids.difference(tweet_user_ids)

print(list(available_notweet_user_ids))

notweet_user_objs = users_col.find({'id_str': {'$in': list(available_notweet_user_ids)}})

print(sum([user_obj['protected'] is False for user_obj in notweet_user_objs]))
