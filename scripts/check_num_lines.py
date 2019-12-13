import pandas as pd

paths = [r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_tokens.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_glove_100_features.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_lda_100_features.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_textual_features.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets_tokens.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets_glove_100_features.csv",
         r"D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets_ftext_100_features.csv"
         r"D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets_textual_features.csv"
         ]

for path in paths:
    df = pd.read_csv(path, header=0)
    print(df.shape)
