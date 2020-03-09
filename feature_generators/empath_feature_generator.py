import csv
import sys
import time
import os
import gensim
import helper
from empath import Empath



ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

lexicon = Empath()


def vectorize_docs(dataset_tokens_path, features_path):

    if not os.path.exists(features_path):

        print('started records generation')
        start = time.time()

        with open(features_path, 'w', newline='', encoding='utf-8') as wf:
            csv_writer = csv.writer(wf, delimiter=',')
            csv_writer.writerow(['empath_' + key for key in sorted(lexicon.cats.keys())])

            with open(dataset_tokens_path, 'r', encoding='utf-8') as rf:
                csv_reader = csv.DictReader(rf, delimiter=',')

                for i, row in enumerate(csv_reader):
                    if i % 100 == 0:
                        print('write csv row', i)
                    tokens = [x.lower() for x in row['tokens_joined'].split() if not helper.stop_or_mention(x)]
                    empath_dict = lexicon.analyze(tokens, normalize=True)
                    empath_vector = [empath_dict[key] for key in sorted(lexicon.cats.keys())]
                    csv_writer.writerow(empath_vector)

        end = time.time()
        print('generated {} records in {} sec(c)'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(ALL_TWEETS_PATH)

    file_name, file_ext = os.path.splitext(dataset_path)
    dataset_tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_empath_{}_features.csv'.format(len(lexicon.cats))
    vectorize_docs(dataset_tokens_path, features_path)


# accuracy: sex 78%, race 73% when all singular tweets, iter 20
