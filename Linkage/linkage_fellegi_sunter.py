import recordlinkage
from recordlinkage.base import BaseCompareFeature
from recordlinkage.classifiers import ECMClassifier, KMeansClassifier
import pandas as pd
import unidecode
import re

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside_processed.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside_processed.csv'

def preprocess_name(name, title=False):

    # Remove parethesized content
    name = name.replace(r'\(.*\)', '')

    # Convert accented characters
    name = unidecode.unidecode(name)

    # Replace '-', '_' and '.' with ' ':
    name = name.replace('-', ' ').replace('_', ' ').replace('.', ' ')

    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z ]', '', name)

    # Make lower-case
    name = name.lower()

    # Remove prefix mr., mr , ms , ms., mrs., mrs , miss, sir, dr
    prefix_list = ['mr ', 'ms ', 'mrs ', 'miss ', 'sir ', 'dr ']

    for prefix in prefix_list:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Convert consecutive spaces into single space
    name = re.sub(' +', ' ', name)

    # Finally trim
    name = name.strip()

    # Optionally titlecase
    if title:

        name = name.title()

    return name

def get_token(name, position):

    tokens = name.split()

    if position == 0 and len(tokens) > 0:

        return tokens[0]

    elif position == -1 and len(tokens) > 1:

        return tokens[-1]

    return ''


def get_prefix(name, length):

    if name:

        return name[:length]

    return ''

df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH, header=0, converters={'twitter_name': str,
                                                                     'twitter_handle': str,
                                                                     'sex': str,
                                                                     'race': str,
                                                                     'gen': str,
                                                                     'party': str
                                                                     })
df_voter = pd.read_csv(LINKAGE_VOTER_PATH, header=0, converters={'fname': str,
                                                                 'mname': str,
                                                                 'lname': str,
                                                                 'full_name': str,
                                                                 'sex': str,
                                                                 'race': str,
                                                                 'gen': str,
                                                                 'party': str},)

df_twitter['index_twitter'] = df_twitter.index
# df_twitter['twitter_name'] = df_twitter['twitter_name'].apply(preprocess_name, args=(True, ))
df_twitter['fname'] = df_twitter['twitter_name'].apply(get_token, args=(0, ))
df_twitter['lname'] = df_twitter['twitter_name'].apply(get_token, args=(-1, ))
# df_twitter['twitter_handle'] = df_twitter['twitter_handle'].apply(preprocess_name, args=(False, ))
df_twitter['fname_init'] = df_twitter['fname'].apply(get_prefix, args=(1, ))
df_twitter['lname_init'] = df_twitter['lname'].apply(get_prefix, args=(1, ))
df_twitter['fname_pref'] = df_twitter['fname'].apply(get_prefix, args=(3, ))
df_twitter['lname_pref'] = df_twitter['lname'].apply(get_prefix, args=(3, ))


df_voter['index_voter'] = df_voter.index
# df_voter['fname'] = df_voter['fname'].apply(preprocess_name, args=(True, ))
# df_voter['mname'] = df_voter['mname'].apply(preprocess_name, args=(True, ))
# df_voter['lname'] = df_voter['lname'].apply(preprocess_name, args=(True, ))
# df_voter['flname'] = df_voter[['fname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
# df_voter['full_name'] = df_voter[['fname', 'mname', 'lname']].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)
df_voter['fname_init'] = df_voter['fname'].apply(get_prefix, args=(1, ))
df_voter['lname_init'] = df_voter['lname'].apply(get_prefix, args=(1, ))
df_voter['fname_pref'] = df_voter['fname'].apply(get_prefix, args=(3, ))
df_voter['lname_pref'] = df_voter['lname'].apply(get_prefix, args=(3, ))

# print(df_twitter['voter_serial'])
# print(df_voter['voter_serial'])


# Set true links
joined_df = pd.merge(df_twitter, df_voter, how='inner', on=['voter_serial'])

print(joined_df[['index_twitter', 'index_voter']])

links_true = joined_df.set_index(['index_twitter', 'index_voter']).index
print('num of true links: {}'.format(len(links_true)))

print(links_true)

# Indexing
indexer = recordlinkage.index.BlockIndex(left_on=['orig_city', 'fname_init', 'lname_init'], right_on=['city', 'fname_init', 'lname_init'])
links_candidate = indexer.index(df_twitter, df_voter)
print('num of candidate links: {}'.format(len(links_candidate)))

# Comparison
comparator = recordlinkage.Compare()

comparator.exact('fname', 'fname', label='fname')
comparator.exact('lname', 'lname', label='lname')

comparator.exact('fname_pref', 'fname_pref', label='fname_pref')
comparator.exact('lname_pref', 'lname_pref', label='lname_pref')

comparator.string('fname', 'fname', method='cosine', label='fname_qgram')
comparator.string('lname', 'lname', method='cosine', label='lname_qgram')

comparator.string('twitter_handle', 'fname', method='cosine',label='handle_fname_qgram')
comparator.string('twitter_handle', 'lname', method='cosine', label='handle_lname_qgram')

comparator.exact('pred_gen', 'gen', label='gen')
comparator.exact('pred_sex', 'sex', label='sex')
comparator.exact('pred_race', 'race', label='race')
comparator.exact('pred_party', 'party', label='party')

comparison_vectors = comparator.compute(links_candidate, df_twitter, df_voter)

# print(comparison_vectors)

# Classification
classifier = ECMClassifier(binarize=0.5)
classifier.fit(comparison_vectors)
links_pred = classifier.predict(comparison_vectors)
print('Num. of many-to-many predicted links: {}'.format(len(links_pred)))

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

cm = recordlinkage.confusion_matrix(links_true, links_pred, total=len(df_twitter) * len(df_voter))
print('TP: {}\nFN: {}\nFP: {}\nTN: {}\n'.format(cm[0][0], cm[0][1], cm[1][0], cm[1][1]))

# compute the F-score for this classification
fscore = recordlinkage.fscore(cm)
print('F-score: {:.2f}'.format(fscore))
recall = recordlinkage.recall(links_true, links_pred)
print('Recall: {:.2f}'.format(recall))
precision = recordlinkage.precision(links_true, links_pred)
print('Precision: {:.2f}'.format(precision))

print(classifier.log_weights)