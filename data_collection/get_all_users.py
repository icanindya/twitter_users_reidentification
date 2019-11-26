import helper

root_twitter_ids = set()
net_twitter_ids = set()

mongo_client = helper.get_mongo_client()

twitter_db = mongo_client['twitter']
users_col = twitter_db['users']
followers_col = twitter_db['followers5k']
followings_col = twitter_db['following5k']

users = users_col.find({})

for user in users:
    root_twitter_ids.add(user['id_str'])

print('root users', len(root_twitter_ids))

followers = followers_col.find({})

for follower in followers:
    net_twitter_ids.update(follower['f_ids'])

print('follower users', len(net_twitter_ids))

followings = followings_col.find({})

for following in followings:
    net_twitter_ids.update(following['f_ids'])

print('follwer + following users', len(net_twitter_ids))

net_twitter_ids = net_twitter_ids.difference(root_twitter_ids)

print('only network users', len(net_twitter_ids))

with open(r'D:\Data\Linkage\FL\FL18\users\network_users.txt', 'w') as wf:
    for twitter_id in net_twitter_ids:
        wf.write('{}\n'.format(twitter_id))


