import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.offsetbox import AnchoredText


ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
selected_ids = ids_df['twitter_id'].values
df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets'])
df = df.loc[df['twitter_id'].isin(selected_ids)]
frequencies = df['num_tweets'].values

frequencies[frequencies > 3200] = 3200

print(min(frequencies), max(frequencies))

# frequencies = np.asarray([2,5,8,5,6,7,8,9,0,1,3,4,6,7,8,9,5,5,8])

# An "interface" to matplotlib.axes.Axes.hist() method
n, bins, patches = plt.hist(x=frequencies, bins=range(50, 3200 + 100, 100), color='#2952a3',
                            alpha=1.0, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Number of Tweets')
plt.ylabel('Frequency')
maxfreq = n.max()
# Set a clean upper y-axis limit.
plt.xlim(xmin=40, xmax=3210)
plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)

anchored_text = AnchoredText('min = 50\nmax = 3200\nbin size = 100', loc=1)
ax = plt.gca()
ax.add_artist(anchored_text)
plt.show()