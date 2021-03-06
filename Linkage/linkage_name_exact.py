import recordlinkage
from recordlinkage.base import BaseCompareFeature
from recordlinkage.classifiers import ECMClassifier, KMeansClassifier
import pandas as pd
import re
import sys
import numpy as np

import warnings
warnings.filterwarnings('ignore')

name_thres = 0.5
handle_thres = 0.5

if len(sys.argv) > 1:
    name_thres = float(sys.argv[1])
    handle_thres = float(sys.argv[1])


pat = re.compile(r'[^a-zA-Z ]+')


def convert_twitter_name(name):

    name = name.lower()
    name = re.sub(pat, '', name)
    name = ' '.join(name.split())

    if name == '':
        name = '-'

    return name


def convert_voter_name(name):

    name = name.lower()
    name = re.sub(pat, '', name)
    name = ' '.join(name.split())

    return name


def get_prefix3(name):
    return name[:3]


def inrange_compare(x, y):

    toks = x.split('-')
    start = int(toks[0])
    end = int(toks[1])

    return int(start <= y <= end)


def inrange(comparator, *args, **kwargs):

    compare = InRange(*args, **kwargs)
    comparator.add(compare)

    return comparator


class InRange(BaseCompareFeature):
    """
    This class is used to compare if one is in range of the other. The similarity
    is 1 in case of agreement and 0 otherwise.

    Parameters
    ----------

    left_on : str or int
        Field name to compare in left DataFrame.
    right_on : str or int
        Field name to compare in right DataFrame.

    """

    name = "inrange"
    description = "Compare one is in range of the other."

    def __init__(self,
                 left_on,
                 right_on,
                 left_is_range = True,
                 label=None):
        super(InRange, self).__init__(left_on, right_on, label=label)
        self.left_is_range = left_is_range

    def _compute_vectorized(self, s_left, s_right):
        if self.left_is_range:
            return np.vectorize(inrange_compare)(s_left, s_right)
        else:
            return np.vectorize(inrange_compare)(s_right, s_left)

DS_TWITTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside_att.csv"
DS_VOTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv"

df_twitter = pd.read_csv(DS_TWITTERSIDE_PATH, header=0, converters={'twitter_name': str, 'twitter_handle': str})

df_twitter['twitter_name'] = df_twitter['twitter_name'].apply(convert_twitter_name)
df_twitter['twitter_handle'] = df_twitter['twitter_handle'].apply(convert_twitter_name)
df_twitter['twitter_name_pref'] = df_twitter['twitter_name'].apply(get_prefix3)
df_twitter['index_twitter'] = df_twitter.index


df_voter = pd.read_csv(DS_VOTERSIDE_PATH, header=0)

df_voter.fillna({'yob': 0}, inplace=True)
df_voter['yob'] = df_voter['yob'].astype(int)

df_voter['fname'] = df_voter['fname'].astype(str)
df_voter['fname'] = df_voter['fname'].apply(convert_voter_name)

df_voter['mname'] = df_voter['mname'].astype(str)
df_voter['mname'] = df_voter['mname'].apply(convert_voter_name)

df_voter['lname'] = df_voter['lname'].astype(str)
df_voter['lname'] = df_voter['lname'].apply(convert_voter_name)

df_voter['flname'] = df_voter['fname'].astype(str) + ' ' + df_voter['lname'].astype(str)
df_voter['flname'] = df_voter['flname'].apply(convert_voter_name)

df_voter['fmlname'] = df_voter['fname'].astype(str) + ' ' + df_voter['mname'].astype(str) + ' ' + df_voter['lname'].astype(str)
df_voter['fmlname'] = df_voter['fmlname'].apply(convert_voter_name)

df_voter['flname_pref'] = df_voter['flname'].apply(get_prefix3)

df_voter['index_voter'] = df_voter.index

num_all_comparisons = len(df_twitter) * len(df_voter)

links_true = pd.merge(df_twitter, df_voter, how='inner', on=['voter_serial']).set_index(['index_twitter', 'index_voter']).index

print('Num. of true links:', len(links_true))

# filtering for unique names

# twitter_name_vc = df_twitter['twitter_name'].value_counts()
# unique_twitter_names = set(twitter_name_vc[twitter_name_vc == 1].index.values)
# df_twitter = df_twitter[df_twitter['twitter_name'].isin(unique_twitter_names)]
# print(len(df_twitter))

# voter_flname_vc = df_voter['flname'].value_counts()
# unique_voter_flnames = set(voter_flname_vc[voter_flname_vc == 1].index.values)
# df_voter = df_voter[df_voter['flname'].isin(unique_voter_flnames)]
# print(len(df_voter))

# indexer = recordlinkage.index.FullIndex()
indexer = recordlinkage.index.BlockIndex(left_on=['pred_sex', 'pred_race', 'pred_party', 'pred_city', 'twitter_name_pref'], right_on=['sex', 'race', 'party', 'city', 'flname_pref'])
# indexer = recordlinkage.index.BlockIndex(left_on=['birthday', 'city'], right_on=['birthday', 'city'])
# indexer = recordlinkage.index.SortedNeighbourhoodIndex(left_on='twitter_name', right_on='flname', window=11)
links_candidate = indexer.index(df_twitter, df_voter)

print('Num. of candidate links:', len(links_candidate))

comparator = recordlinkage.Compare()
comparator.inrange = inrange


comparator.exact('twitter_name', 'fname', label='tname_fname_exact')
comparator.exact('twitter_name', 'flname', label='tname_flname_exact')

comparator.string('twitter_name', 'fname', method='qgram', label='tname_fname_qgram')
comparator.string('twitter_name', 'flname', method='qgram', label='tname_flname_qgram')

comparator.string('twitter_handle', 'fname', method='qgram', label='handle_fname_qgram')
comparator.string('twitter_handle', 'flname', method='qgram', label='handle_flname_qgram')

# comparator.string('twitter_name', 'flname', method='jarowinkler', label='tname_flname_jw')
# comparator.exact('pred_sex', 'sex', label='sex')
# comparator.exact('pred_race', 'race', label='race')
comparator.inrange(comparator, 'pred_yob', 'yob', left_is_range=True, label='yob_range')
# comparator.exact('pred_party', 'party', label='party')
# comparator.exact('pred_city', 'city', label='city')

comparison_vectors = comparator.compute(links_candidate, df_twitter, df_voter)

print(comparison_vectors.iloc[0])

# comparison_vectors['tname_fname_qgram'] = comparison_vectors['tname_fname_qgram'].apply(lambda x: 1 if x >= 0.5 else 0)
# comparison_vectors['tname_flname_qgram'] = comparison_vectors['tname_flname_qgram'].apply(lambda x: 1 if x >= 0.5 else 0)
# comparison_vectors['handle_fname_qgram'] = comparison_vectors['handle_fname_qgram'].apply(lambda x: 1 if x >= 0.5 else 0)
# comparison_vectors['handle_flname_qgram'] = comparison_vectors['handle_flname_qgram'].apply(lambda x: 1 if x >= 0.5 else 0)


# Classification step

# Use basic classifier
# threshold = 4
# links_pred = comparison_vectors[comparison_vectors.sum(axis=1) == threshold].index

# Use classification algorithm
classifier = ECMClassifier(binarize=0.5)
classifier.fit(comparison_vectors)
links_pred = classifier.predict(comparison_vectors)

# print(links_pred)

print('Num. of many-to-many predicted links: {}'.format(len(links_pred)))

# Take the first match for each Twitter user
# links_pred = links_pred.to_frame().groupby(level=0, axis=0).head(1).index

# Take the match with highest probability for each Twitter user
links_prob = classifier.prob(comparison_vectors)
links_prob = links_prob[links_prob.index.isin(links_pred.values)]
links_prob = links_prob.to_frame()
links_prob.index.names = ['index_twitter', 'index_voter']
links_prob.columns = ['match_prob']
links_prob.reset_index(inplace=True)
links_prob = links_prob.sort_values('match_prob', ascending=False).drop_duplicates('index_twitter')
links_prob.set_index(['index_twitter', 'index_voter'], inplace=True)
links_pred = links_prob.index

print('Num. of many-to-one predicted links: {}'.format(len(links_pred)))


cm = recordlinkage.confusion_matrix(links_true, links_pred, total=num_all_comparisons)
print('TP: {}\nFN: {}\nFP: {}\nTN: {}\n'.format(cm[0][0], cm[0][1], cm[1][0], cm[1][1]))


# compute the F-score for this classification
fscore = recordlinkage.fscore(cm)
print('F-score: {:.2f}'.format(fscore))
recall = recordlinkage.recall(links_true, links_pred)
print('Recall: {:.2f}'.format(recall))
precision = recordlinkage.precision(links_true, links_pred)
print('Precision: {:.2f}'.format(precision))

print(classifier.log_weights)









