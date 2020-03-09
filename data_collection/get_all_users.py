import helper

import matplotlib.pyplot as plt
from matplotlib_venn import venn3, venn3_circles
import numpy as np

root_twitter_ids = set()
follower_twitter_ids = set()
following_twitter_ids = set()
net_twitter_ids = set()

mongo_client = helper.get_mongo_client()

twitter_db = mongo_client['twitter']
truths_col = twitter_db['ground_truths']
followers_col = twitter_db['followers5k']
followings_col = twitter_db['following5k']

truths = truths_col.find({})

root_twitter_ids.update([truth['twitter_id'] for truth in truths])

print('root_twitter_ids', len(root_twitter_ids))

followers = followers_col.find({})

for follower in followers:
    follower_twitter_ids.update(follower['f_ids'])

print('follower_twitter_ids', len(follower_twitter_ids))

followings = followings_col.find({})

for following in followings:
    following_twitter_ids.update(following['f_ids'])

print('following_twitter_ids', len(following_twitter_ids))

only_root_twitter_ids = root_twitter_ids.difference(follower_twitter_ids).difference(following_twitter_ids)
only_follower_twitter_ids = follower_twitter_ids.difference(root_twitter_ids).difference(following_twitter_ids)
only_following_twitter_ids = following_twitter_ids.difference(root_twitter_ids).difference(follower_twitter_ids)
root_follower_following_twitter_ids = root_twitter_ids.intersection(follower_twitter_ids).intersection(following_twitter_ids)
only_root_follower_twitter_ids = root_twitter_ids.intersection(follower_twitter_ids).difference(root_follower_following_twitter_ids)
only_root_following_twitter_ids = root_twitter_ids.intersection(following_twitter_ids).difference(root_follower_following_twitter_ids)
only_follower_following_twitter_ids = follower_twitter_ids.intersection(following_twitter_ids).difference(root_follower_following_twitter_ids)

print('only_root_twitter_ids', len(only_root_twitter_ids))
print('only_follower_twitter_ids', len(only_follower_twitter_ids))
print('only_following_twitter_ids', len(only_following_twitter_ids))
print('root_follower_following_twitter_ids', len(root_follower_following_twitter_ids))
print('only_root_follower_twitter_ids', len(only_root_follower_twitter_ids))
print('only_root_following_twitter_ids', len(only_root_following_twitter_ids))
print('only_follower_following_twitter_ids', len(only_follower_following_twitter_ids))


only_network_twitter_ids = follower_twitter_ids.union(following_twitter_ids).difference(root_twitter_ids)

print('only_network_twitter_ids', len(only_network_twitter_ids))

# v=venn3(subsets = (len(only_root_twitter_ids), len(only_following_twitter_ids),
#                    len(only_root_following_twitter_ids), len(only_follower_twitter_ids),
#                    len(only_root_follower_twitter_ids), len(only_follower_following_twitter_ids),
#                    len(root_follower_following_twitter_ids)), set_labels = ('Root Users', 'Friends', 'Followers'))
out=venn3_circles(subsets = (len(only_root_twitter_ids), len(only_following_twitter_ids),
                   len(only_root_following_twitter_ids), len(only_follower_twitter_ids),
                   len(only_root_follower_twitter_ids), len(only_follower_following_twitter_ids),
                   len(root_follower_following_twitter_ids)), linestyle='dashed', linewidth=1, color="grey")

# for idx, subset in enumerate(out.subset_labels):
#     out.subset_labels[idx].set_visible(False)

# plt.annotate('Unknown set', xy=v.get_label_by_id('100').get_position() - np.array([0, 0.05]), xytext=(-70,-70),
#              ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
#              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray'))
#
# plt.annotate('{}'.format(len(root_follower_following_twitter_ids)), xy=v.get_label_by_id('111').get_position() - np.array([0, 0.05]), xytext=(-70,-70),
#              ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
#              arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray'))

plt.show()


# with open(r'D:\Data\Linkage\FL\FL18\users\network_users.txt', 'w') as wf:
#     for twitter_id in net_twitter_ids:
#         wf.write('{}\n'.format(twitter_id))


