import sys
import os
import csv
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

LDA_FEATURES_SIZE = 100
N_TOP_WORDS = 20

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'
MODEL_TOKENS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\user_tweets_tokens.csv'
MODEL_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\user_tweets_ldask_{}.model'.format(LDA_FEATURES_SIZE)
DICTIONARY_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\user_tweets_ldask.dictionary'


def print_top_words(model, feature_names, n_top_words):

    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()


def get_model():

    if os.path.exists(MODEL_PATH):
        print('loading prebuilt model')
        tf_feature_names = joblib.load(DICTIONARY_PATH)
        lda_model = joblib.load(MODEL_PATH)
        print('loaded prebuilt model')
    else:
        class Corpus(object):

            def __iter__(self):
                with open(MODEL_TOKENS_PATH, 'r', encoding='utf-8') as rf:
                    csv_reader = csv.DictReader(rf, delimiter=',')
                    for i, row in enumerate(csv_reader):
                        if i % 100000 == 0:
                            print('read csv row for model', i)
                        yield row['tokens_joined']

        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=100, max_features=50000, stop_words='english')
        tf = tf_vectorizer.fit_transform(Corpus().__iter__())
        tf_feature_names = tf_vectorizer.get_feature_names()
        lda_model = LatentDirichletAllocation(n_components=LDA_FEATURES_SIZE, max_iter=10)
        lda_model.fit(tf)
        joblib.dump(tf_feature_names, DICTIONARY_PATH)
        joblib.dump(lda_model, MODEL_PATH)

    print("\nTopics in LDA model:")

    print_top_words(lda_model, tf_feature_names, n_top_words=N_TOP_WORDS)

    return lda_model


if __name__ == '__main__':

    option = '1'

    if len(sys.argv) > 1:
        option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_ldask_{}_features.csv'.format(LDA_FEATURES_SIZE)

    model = get_model()

    # vectorize_docs(dictionary, model, dataset_tokens_path, features_path)