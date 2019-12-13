import pandas as pd

input_col_names = ['twitter_id', 'doc', 'dob_or_age', 'sex', 'race_code', 'zip_code', 'city', 'party']
df = pd.read_csv(r'D:\Data\Linkage\FL\FL18\tweets\yearly_tweets_combined.csv', encoding='utf-8', names=input_col_names)
df = df[['twitter_id', 'dob_or_age']]

sample = df.sample(n=50, random_state=0)

print(sample)
