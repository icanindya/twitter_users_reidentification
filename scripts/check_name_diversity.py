import pandas as pd
import re

pat = re.compile(r'[^a-zA-Z ]+')


def convert_name(name):

    name = name.lower()
    name = re.sub(pat, '', name)
    name = ' '.join(name.split())

    return name

DS_TWITTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_twitterside.csv"
DS_VOTERSIDE_PATH = r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv"

df_voter = pd.read_csv(DS_VOTERSIDE_PATH, header=0)

df_voter['full_name'] = df_voter['fname'] + ' ' + df_voter['mname'] + df_voter['lname']
df_voter['full_name'] = df_voter['full_name'].astype(str).apply(lambda x: x.lower())

df_voter['flname'] = df_voter['fname'] + ' ' + df_voter['lname']
df_voter['flname'] = df_voter['flname'].astype(str).apply(lambda x: x.lower())

df_voter['fname'] = df_voter['fname'].astype(str).apply(lambda x: x.lower())

unique_full_names = df_voter['full_name'].value_counts()[df_voter['full_name'].value_counts() == 1]
unique_flnames = df_voter['flname'].value_counts()[df_voter['flname'].value_counts() == 1]
unique_fnames = df_voter['fname'].value_counts()[df_voter['fname'].value_counts() == 1]

print(len(unique_full_names)/len(df_voter))
print(len(unique_flnames)/len(df_voter))
print(len(unique_fnames)/len(df_voter))








