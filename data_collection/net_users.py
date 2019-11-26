import datetime
import time
import helper
import tweepy

RATE_LIMIT = 900
TIME_WINDOW = 900
api_count = 0
begin_timestamp = 0
end_timestamp = 0

NET_USERS_PATH = r'D:\Data\Linkage\FL\FL18\users\network_users.txt'


def get_user_index(index_col):
    index = index_col.find_one({}, {'position': 1})
    if not index:
        position = 0
        index = {'position': position}
        index_col.insert_one(index)
    return index['position']


def update_user_index(index_col, position):
    query = index_col.find_one()
    newvalues = {'$set': {'position': position}}
    index_col.update_one(query, newvalues)


def store_users(users_col, user_jsons):
    users_col.insert_many(user_jsons)


def get_users(apis, user_ids):

    global RATE_LIMIT, TIME_WINDOW, api_count, begin_timestamp, end_timestamp

    error = True

    while error:

        chosen_api = apis[api_count % len(apis)]
        api_count += 1

        if api_count % (RATE_LIMIT * len(apis)) == 1:
            begin_timestamp = time.time()

        elif api_count % (RATE_LIMIT * len(apis)) == 0:
            end_timestamp = time.time()
            elapsed_seconds = end_timestamp - begin_timestamp
            if elapsed_seconds < TIME_WINDOW + 5:
                now = datetime.datetime.now()
                then = now + datetime.timedelta(seconds=TIME_WINDOW + 5 - elapsed_seconds)
                print('Going to sleep for {} second(s). Will resume at {}:{}:{}.'.format(
                    int(TIME_WINDOW + 5 - elapsed_seconds), then.hour, then.minute, then.second))
                time.sleep(TIME_WINDOW + 5 - elapsed_seconds)

        try:
            user_objs = chosen_api.lookup_users(user_ids)
            user_jsons = [user_obj._json for user_obj in user_objs]
            error = False

        except tweepy.TweepError as te:
            print('Going to sleep for 5 seconds. Tweepy error: {}'.format(te.reason))
            time.sleep(5)

    return user_jsons


if __name__ == '__main__':

    found_users = 0

    apis = helper.get_twitter_user_apis()
    mongo_client = helper.get_mongo_client()

    twitter_db = mongo_client['twitter']
    age_labels_col = twitter_db['age_labels']
    users_col = twitter_db['net_users']
    user_index_col = twitter_db['net_users_index']

    user_ids = []

    with open(NET_USERS_PATH, 'r') as rf:
        for line in rf:
            user_ids.append(line.strip())

    last_user_position = get_user_index(user_index_col)

    curr_user_position = last_user_position

    while curr_user_position < len(user_ids):
        print('curr user postion: {}'.format(curr_user_position))
        curr_user_ids = user_ids[curr_user_position:min(curr_user_position + 100, len(user_ids))]
        user_jsons = get_users(apis, curr_user_ids)
        store_users(users_col, user_jsons)
        found_users += len(user_jsons)
        curr_user_position += len(curr_user_ids)
        update_user_index(user_index_col, curr_user_position)

    print('found users:', found_users)
