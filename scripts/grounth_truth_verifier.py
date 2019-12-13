import random
import helper

mclient = helper.get_mongo_client()

twitter_db = mclient['twitter']
ground_truths_col = twitter_db['ground_truths']
voters_col = twitter_db['voters']
users_col = twitter_db['users']

ground_truths = ground_truths_col.find({})

pairs = []

count = 0

for gt in ground_truths:
    count += 1
    #    print(count, gt['voter_serial'], gt['twitter_id'])
    voter = voters_col.find_one({'serial': gt['voter_serial']})
    user = users_col.find_one({'id_str': gt['twitter_id']})

    if voter and user:
        voter_name_parts = [voter['fname'], voter['mname'], voter['lname']]
        voter_name = ' '.join([x for x in voter_name_parts if x])
        voter_email = voter['email']
        user_name = user['name']
        user_handle = user['screen_name']

        pairs.append((voter_name, user_name, user_handle, voter_email))

random.seed(16189)
samp = random.sample(pairs, 500)

print(len(pairs))

for pair in samp:
    print('{} -- {} ------------------------------ {} -- {}'.format(pair[0], pair[1], pair[2], pair[3]))
