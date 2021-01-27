import pandas as pd

twitter_file = r"D:\Data\Linkage\FL\FL18\linkage\twitterside.csv"
twitter_city_file = r"D:\Data\Linkage\FL\FL18\linkage\twitterside_brandon.csv"

df = pd.read_csv(twitter_file, header=0)

df = df.loc[df['orig_city'] == 'brandon']

df.to_csv(twitter_city_file, index=False)