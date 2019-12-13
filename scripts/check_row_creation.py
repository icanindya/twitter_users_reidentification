import pandas as pd

file_path = r"D:\Data\Linkage\FL\FL18\row_creation\all_tweets.csv"
df = pd.read_csv(file_path, header=0, nrows=10)

for i, row in df.iterrows():
    print(
        row['twitter_id'], row['voter_serial'], row['dob'], row['age'], row['sex'], row['race_code'],
        row['zip_code'], row['city'], row['party'], row['tweet_startdate'], row['tweet_enddate'],
        row['num_tweets'], row['num_hashtags'], row['user_mentions'], row['num_urls'],
        row['num_media'], row['num_symbols'], row['num_polls']
    )
