import helper
import numpy as np
import collections
import matplotlib.ticker as ticker
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt


mongo_client = helper.get_mongo_client()
twitter_db = mongo_client['twitter']
truths_col = twitter_db['ground_truths']
voters_col = twitter_db['voters']

selected_truths = list(truths_col.find({}))

selected_tids = [selected_gt['twitter_id'] for selected_gt in selected_truths]

selected_vsers = [selected_gt['voter_serial'] for selected_gt in selected_truths]

voters = voters_col.find({'serial': {'$in': selected_vsers}})

age_dict = collections.defaultdict(int)
sex_dict = collections.defaultdict(int)
race_dict = collections.defaultdict(int)
party_dict = collections.defaultdict(int)

for voter in voters:

    try:
        age_dict[helper.get_curr_age_label(voter['dob'])] += 1
    except:
        print('invalid dob: {}'.format(voter['dob']))

    try:
        if voter['sex'] in ['M', 'F', 'U']:
            sex_dict[voter['sex']] += 1
    except:
        print('invalid sex: {}'.format(voter['sex']))

    try:
        short_race = helper.get_short_race(voter['race_code'])
        if short_race is not None:
            race_dict[short_race] += 1
    except:
        print('invalid race: {}'.format(voter['race_code']))

    try:
        short_party = helper.get_short_party(voter['party'])
        if short_party is not None:
            party_dict[short_party] += 1
    except:
        print('invalid party: {}'.format(voter['party']))

# print(len(yobs))

#credit https://matplotlib.org/devdocs/gallery/pie_and_po
age_labels = list(age_dict.keys())
age_counts = list(age_dict.values())

sex_labels = list(sex_dict.keys())
sex_counts = list(sex_dict.values())

race_labels = list(race_dict.keys())
race_counts = list(race_dict.values())

party_labels = list(party_dict.keys())
party_counts = list(party_dict.values())

fig, axs = plt.subplots(2, 2)

plt.subplot(the_grid[0, 0], aspect=1, title='Age-group Distribution')
flavor_pie = plt.pie(age_counts, labels=age_labels, shadow=False, colors=colors)

plt.subplot(the_grid[0, 1], aspect=1, title='Sex Distribution')
flavor_pie = plt.pie(sex_counts, labels=sex_labels, shadow=False, colors=colors)

plt.subplot(the_grid[1, 0], aspect=1, title='Race Distribution')
flavor_pie = plt.pie(race_counts, labels=race_labels, shadow=False, colors=colors)

plt.subplot(the_grid[1, 1], aspect=1, title='Party Distribution')
flavor_pie = plt.pie(party_counts, labels=party_labels, shadow=False, colors=colors)

plt.suptitle('Attribute Distribution', fontsize=16)

plt.show()
