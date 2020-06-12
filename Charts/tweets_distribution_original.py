import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import matplotlib.ticker as tick

NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)
ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'

def reformat_large_tick_values(tick_val, pos):
    """
    Turns large tick values (in the billions, millions and thousands) such as 4500 into 4.5K and also appropriately turns 4000 into 4K (no zero after the decimal).
    """
    if tick_val >= 1000000000:
        val = round(tick_val / 1000000000, 1)
        new_tick_format = '{:}B'.format(val)
    elif tick_val >= 1000000:
        val = round(tick_val / 1000000, 1)
        new_tick_format = '{:}M'.format(val)
    elif tick_val >= 1000:
        val = round(tick_val / 1000, 1)
        new_tick_format = '{:}K'.format(val)
    elif tick_val < 1000:
        new_tick_format = round(tick_val, 1)
    else:
        new_tick_format = tick_val

    # make new_tick_format into a string value
    new_tick_format = str(new_tick_format)

    # code below will keep 4.5M as is but change values such as 4.0M to 4M since that zero after the decimal isn't needed
    index_of_decimal = new_tick_format.find(".")

    if index_of_decimal != -1:
        value_after_decimal = new_tick_format[index_of_decimal + 1]
        if value_after_decimal == "0":
            # remove the 0 after the decimal point since it's not needed
            new_tick_format = new_tick_format[0:index_of_decimal] + new_tick_format[index_of_decimal + 2:]

    return new_tick_format


step1 = 25
step2 = 25

df_ids = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
selected_ids = df_ids['twitter_id'].tolist()
df = pd.read_csv(ALL_TWEETS_PATH, header=0, usecols=['twitter_id', 'num_tweets'])

# min_tweets = df['num_tweets'].min()
# max_tweets = df['num_tweets'].max()
#
# if max_tweets % step1 != 0:
#
#     max_tweets = ((max_tweets // step1) + 1) * step1
#
# print(min_tweets, max_tweets)
#
# x1 = [v for v in range(min_tweets, max_tweets + 1, step1)]
# y1 = []
#
# for v in x1:
#     y1.append(len(df.loc[(df['num_tweets'] >= v)]))


df = df.loc[df['twitter_id'].isin(selected_ids)]

min_tweets = df['num_tweets'].min()
max_tweets = min(3200, df['num_tweets'].max())

if max_tweets % step2 != 0:
    max_tweets = ((max_tweets // step2) + 1) * step2

print(min_tweets, max_tweets)

x2 = [v for v in range(min_tweets, max_tweets + 1, step2)]
y2 = []

for v in x2:
    y2.append(len(df.loc[df['num_tweets'] <= v]))





fig = plt.figure()


# ax1 = fig.add_subplot(211)
# color_vals1 = [(v/max(y1))*0.7 for v in y1]
# colors1 = cm.get_cmap('YlOrRd')(color_vals1)
# ax1.bar(x1, y1, width=step, color=colors1)
# ax1.set_title('Cumulative distribution of the num. of tweets per row')
# ax1.set_ylabel('Num. of rows')
# ax1.set_xlabel('Num. of tweets per row')

min_x2 = min(x2)
max_x2 = max(x2)
max_y2 = max(y2)
tick_step = 450
max_tick = max_x2
if (max_x2 - min_x2) % tick_step != 0:
    max_tick = (((max_x2 - min_x2) // tick_step) + 1) * tick_step

ax2 = fig.add_subplot(111)
ax2.get_yaxis().set_major_formatter(tick.FuncFormatter(reformat_large_tick_values))
color_vals2 = [(v/max_y2)*0.65 for v in y2]
colors2 = cm.get_cmap('YlOrRd')(color_vals2)
ax2.bar(x2, y2, width=step2, color=colors2)
ax2.set_title('\'Y\' Twitter users have at most \'X\' Tweets')
ax2.set_xlabel('Num. of tweets')
ax2.set_ylabel('Num. of Twitter users')
print(max_tick)

ax2.set_xticks(np.arange(min_x2, max_tick + 80, tick_step))

plt.show()