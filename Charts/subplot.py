import helper
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
import matplotlib.ticker as tick


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


ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
VOTERS_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv"
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)


df_twitter = pd.read_csv(ALL_TWEETS_PATH, header=0)
df_twitter['race'] = df_twitter['race'].apply(helper.get_short_race)
df_twitter['party'] = df_twitter['party'].apply(helper.get_short_party)
df_twitter['dob_1946'] = df_twitter['dob'].apply(lambda x: int(x[-4:]) < 1950)
df_twitter['dob'] = df_twitter['dob'].apply(helper.get_generation)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
selected_ids = ids_df['twitter_id'].tolist()
df_twitter = df_twitter.loc[df_twitter['twitter_id'].isin(selected_ids)]

df_voter = pd.read_csv(VOTERS_PATH, header=0)
df_voter['dob_1946'] = df_voter['dob'].apply(lambda x: int(x[-4:]) < 1950)
df_voter['dob'] = df_voter['dob'].apply(helper.get_generation)

df_t = df_twitter[df_twitter['dob_1946'] == True]
df_v = df_voter[df_voter['dob_1946'] == True]

print(len(df_t)/len(df_twitter), len(df_v)/len(df_voter))

dob_counts_twitter = df_twitter['dob'].value_counts().to_frame()
sex_counts_twitter = df_twitter['sex'].value_counts().to_frame()
race_counts_twitter = df_twitter['race'].value_counts().to_frame()
party_counts_twitter = df_twitter['party'].value_counts().to_frame()

dob_counts_voter = df_voter['dob'].value_counts().to_frame()
sex_counts_voter = df_voter['sex'].value_counts().to_frame()
race_counts_voter = df_voter['race'].value_counts().to_frame()
party_counts_voter = df_voter['party'].value_counts().to_frame()

dob_counts = pd.merge(dob_counts_twitter, dob_counts_voter, left_index=True, right_index=True, suffixes=('_twitter', '_voter'))
dob_counts.sort_index(ascending=False, inplace=True)
sex_counts = pd.merge(sex_counts_twitter, sex_counts_voter, left_index=True, right_index=True, suffixes=('_twitter', '_voter'))
sex_counts.sort_values(by='sex_twitter', inplace=True, ascending=False)
race_counts = pd.merge(race_counts_twitter, race_counts_voter, left_index=True, right_index=True, suffixes=('_twitter', '_voter'))
race_counts.sort_values(by='race_twitter', inplace=True, ascending=False)
party_counts = pd.merge(party_counts_twitter, party_counts_voter, left_index=True, right_index=True, suffixes=('_twitter', '_voter'))
party_counts.sort_values(by='party_twitter', inplace=True, ascending=False)

axes = []

fig = plt.figure()
ax1 = fig.add_subplot(221)
ax2 = ax1.twinx()
axes.extend([ax1, ax2])

ind = np.arange(len(dob_counts))
width = 0.2

ax1.bar(ind - width/2, dob_counts['dob_twitter'].tolist(), color='lightskyblue', alpha= 0.8, width=width, label='Twitter Users')
ax2.bar(ind + width/2, dob_counts['dob_voter'].tolist(), color='steelblue', alpha=0.8, width=width, label='FL Voters')

ax1.set_xticks(ind)
ax1.set_xticklabels(dob_counts.index.tolist())

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper center', ncol=2)
ax1.set_xlabel('Generation')

ax1 = fig.add_subplot(222)
ax2 = ax1.twinx()
axes.extend([ax1, ax2])

ind = np.arange(len(sex_counts))
width = 0.04

ax1.bar(ind - width/2, sex_counts['sex_twitter'].tolist(), color='pink', alpha= 0.8, width=width, label='Twitter Users')
ax2.bar(ind + width/2, sex_counts['sex_voter'].tolist(), color='palevioletred', alpha=0.8, width=width, label='FL Voters')

ax1.set_xticks(ind)
ax1.set_xticklabels(sex_counts.index.tolist())

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper center', ncol=2)
ax1.set_xlabel('Sex')

ax1 = fig.add_subplot(223)
ax2 = ax1.twinx()
axes.extend([ax1, ax2])

ind = np.arange(len(race_counts))
width = 0.3

ax1.bar(ind - width/2, race_counts['race_twitter'].tolist(), color='lightgreen', alpha= 0.8, width=width, label='Twitter Users')
ax2.bar(ind + width/2, race_counts['race_voter'].tolist(), color='seagreen', alpha=0.8, width=width, label='FL Voters')
# ax2.get_yaxis().get_major_formatter().set_scientific(False)

ax1.set_xticks(ind)
ax1.set_xticklabels(race_counts.index.tolist())

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper center', ncol=2)
ax1.set_xlabel('Race')

ax1.text(0.71, 0.24, ('IA: American Indian or Alaskan Native\n\n'
                   'AP: Asian Or Pacific Islander\n\n'
                   'BL: Black, Not Hispanic\n\n'
                   'HI: Hispanic\n\n'
                   'WH: White, Not Hispanic\n\n'
                   'OT: Other\n\n'
                   'MU: Multi-racial\n\n'
                   'UN: Unknown'
                  ),
         color='black',
         bbox=dict(facecolor='whitesmoke', edgecolor='lightgrey', boxstyle='round'),
         transform=ax1.transAxes,
         fontsize='x-small')


ax1 = fig.add_subplot(224)
ax2 = ax1.twinx()
axes.extend([ax1, ax2])

ind = np.arange(len(party_counts))
width = 0.34

ax1.bar(ind - width/2, party_counts['party_twitter'].tolist(), color='sandybrown', alpha= 0.8, width=width, label='Twitter Users')
ax2.bar(ind + width/2, party_counts['party_voter'].tolist(), color='chocolate', alpha=0.8, width=width, label='FL Voters')

ax1.set_xticks(ind)
ax1.set_xticklabels(party_counts.index.tolist())

handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper center', ncol=2)
ax1.set_xlabel('Party Affiliation')


ax1.text(0.65, 0.17, ('CP: Constitution Party of Florida\n\n'
                   'DM: Florida Democratic Party\n\n'
                   'EC: Ecology Party of Florida\n\n'
                   'GR: Green Party of Florida\n\n'
                   'IN: Independent Party of Florida\n\n'
                   'LP: Libertarian Party of Florida\n\n'
                   'NP: No Party Affiliation\n\n'
                   'SL: Party for Socialism and Liberation - Florida\n\n'
                   'RF: Reform Party of Florida\n\n'
                   'RP: Republican Party of Florida'
                  ),
         color='black',
         bbox=dict(facecolor='whitesmoke', edgecolor='lightgrey', boxstyle='round'),
         transform=ax1.transAxes,
         fontsize='x-small')

for ax in axes:
    ax.get_yaxis().set_major_formatter(tick.FuncFormatter(reformat_large_tick_values))
    tot_height = sum([p.get_height() for p in ax.patches])
    max_height = max([p.get_height() for p in ax.patches])
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()

        print(y, height)
        ax.annotate('{:.0%}'.format(height/tot_height), (x, y + height), fontsize='small')
plt.show()