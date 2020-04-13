import unidecode
import re
import pandas as pd

LINKAGE_TWITTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside.csv'
LINKAGE_TWITTER_PROCESSED_PATH = r'D:\Data\Linkage\FL\FL18\linkage\twitterside_processed.csv'
LINKAGE_VOTER_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside.csv'
LINKAGE_VOTER_PROCESSED_PATH = r'D:\Data\Linkage\FL\FL18\linkage\voterside_processed.csv'
CITY_VOTERS_PATH = r'D:\Data\Linkage\FL\FL18\linkage\citywise\voterside_processed_{}.csv'


def preprocess_name(name):

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

    return name


# df_twitter = pd.read_csv(LINKAGE_TWITTER_PATH,
#                          header=0,
#                          converters={'twitter_name': str,
#                                      'twitter_handle': str,
#                                      'orig_fname': str,
#                                      'orig_mname': str,
#                                      'orig_lname': str})
#
# # Preprocess names
# df_twitter['twitter_name'] = df_twitter['twitter_name'].apply(preprocess_name)
# df_twitter['twitter_handle'] = df_twitter['twitter_handle'].apply(preprocess_name)

# df_twitter.to_csv(LINKAGE_TWITTER_PROCESSED_PATH, index=False)


df_voter = pd.read_csv(LINKAGE_VOTER_PATH,
                       header=0,
                       converters={'fname': str, 'mname': str,
                                   'lname': str, 'sex': str,
                                   'race': str, 'dob': str,
                                   'party': str, 'city': str})

# Only keep voters born after 1945
df_voter = df_voter.loc[df_voter['dob'].apply(lambda x: int(x[-4:])) > 1945]

# Preprocess names
df_voter['fname'] = df_voter['fname'].apply(preprocess_name)
df_voter['mname'] = df_voter['mname'].apply(preprocess_name)
df_voter['lname'] = df_voter['lname'].apply(preprocess_name)
df_voter.insert(4, 'full_name', df_voter[['fname', 'mname', 'lname']].agg(lambda names: ' '.join([n for n in names if n]), axis=1))

df_voter.to_csv(LINKAGE_VOTER_PROCESSED_PATH, index=False)


df_voter = pd.read_csv(LINKAGE_VOTER_PROCESSED_PATH, header=0, converters={'city': str})

# city_voters_dict = {}

for city in df_voter['city'].unique():

    city = city.strip().replace('/', '+')

    if city not in ['', '*']:

        df_city_voters = df_voter.loc[df_voter['city'] == city]
        df_city_voters.to_csv(CITY_VOTERS_PATH.format(city), index=False)





