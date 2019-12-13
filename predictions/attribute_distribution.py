import helper
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def change_width(ax, new_value):
    for patch in ax.patches:
        current_width = patch.get_width()

        print(current_width)

        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)


ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
NUM_TWEETS = 50
SELECTED_TWITTER_IDS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\twitter_ids_{}_tweets.csv'.format(NUM_TWEETS)


df = pd.read_csv(ALL_TWEETS_PATH, header=0)
df['sex'] = df['sex'].apply(lambda x: 'F' if x not in ['M', 'F'] else x)
df['race_code'] = df['race_code'].apply(helper.get_text_race_code)
df['party'] = df['party'].apply(helper.get_short_party)

ids_df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test_ids_df = ids_df.sample(frac=helper.test_percentage, random_state=helper.random_seed)
test_ids = test_ids_df['twitter_ids'].tolist()
train_ids_df = ids_df.drop(test_ids_df.index)
train_ids = train_ids_df['twitter_ids'].tolist()

# train_df = df.loc[df['twitter_id'].isin(train_ids)]
# test_df = df.loc[df['twitter_id'].isin(test_ids)]
# print(train_df['sex'].value_counts())
# print(test_df['sex'].value_counts())

train_test_ids = train_ids + test_ids
train_test_df = df.loc[df['twitter_id'].isin(train_test_ids)]

sex_counts = train_test_df['sex'].value_counts()
race_counts = train_test_df['race_code'].value_counts()
party_counts = train_test_df['party'].value_counts()

df = pd.read_csv(YEARLY_TWEETS_PATH, header=0)
df['age'] = df['age'].apply(helper.get_maif_age_label)
train_test_df = df.loc[df['twitter_id'].isin(train_test_ids)]
age_counts = train_test_df['age'].value_counts()

fig, axs = plt.subplots(1, 4, squeeze=False)
sns.set_style('whitegrid')


sns.barplot(age_counts.index, age_counts.values, alpha=0.8, palette=sns.light_palette('purple', reverse=True), ax=axs[0][0])
axs[0][0].set_ylabel('Num. of Occurances')
axs[0][0].set_xlabel('Age-group')


sns.barplot(sex_counts.index, sex_counts.values, alpha=0.8, palette=sns.light_palette('seagreen', reverse=True), ax=axs[0][1])
axs[0][1].set_xlabel('Sex')


sns.barplot(race_counts.index, race_counts.values, alpha=0.8, palette=sns.light_palette('darkorange', n_colors=8, reverse=True), ax=axs[0][2])
axs[0][2].set_xlabel('Race')


sns.barplot(party_counts.index, party_counts.values, alpha=0.8, palette=sns.light_palette('navy', n_colors=6 , reverse=True), ax=axs[0][3])
axs[0][3].set_xlabel('Party Affiliation')

change_width(axs[0][0], 0.5)
change_width(axs[0][1], 0.2)
change_width(axs[0][2], 0.8)

plt.show()


