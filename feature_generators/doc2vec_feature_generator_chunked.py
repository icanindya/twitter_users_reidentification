import csv
import sys
import time
import os
import gensim
import helper
import pandas as pd

D2V_EMBEDDING_SIZE = 100

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
ALL_TWEETS_CHUNKED_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets_chunked.csv'


def vectorize(tokens_joined, model):

    tokens = [x.lower() for x in tokens_joined.split() if not helper.stop_or_mention(x)]
    d2v_vector = [str(x) for x in model.infer_vector(tokens)]
    return d2v_vector


if __name__ == '__main__':

    dataset_path = ALL_TWEETS_CHUNKED_PATH

    for i in range(1, 7):

        num_tweets = 25 * i

        file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)
        model_path = file_name + '_d2v_{}.model'.format(D2V_EMBEDDING_SIZE)
        model = gensim.models.doc2vec.Doc2Vec.load(model_path)

        file_name, file_ext = os.path.splitext(dataset_path)
        dataset_tokens_path = file_name + '_tokens.csv'

        features_path = file_name + '_d2v_{}_features_{}_tweets.csv'.format(D2V_EMBEDDING_SIZE, num_tweets)

        df = pd.read_csv(dataset_tokens_path, header=0, converters={
            'tokens25_joined': str,
            'tokens50_joined': str,
            'tokens75_joined': str,
            'tokens100_joined': str,
            'tokens125_joined': str,
            'tokensbeyond_joined': str
        })

        df['tokens_joined'] = df[df.columns[:i]].agg(lambda cols: ' '.join([col for col in cols if col]), axis=1)

        df['d2v'] = df['tokens_joined'].apply(vectorize, args=(model,))

        header = ['d2v-{}'.format(i) for i in range(D2V_EMBEDDING_SIZE)]

        df = pd.DataFrame(df['d2v'].values.tolist())

        df.columns = header

        df.to_csv(features_path, index=False)

# accuracy: sex 78%, race 73% when all singular tweets, iter 20
