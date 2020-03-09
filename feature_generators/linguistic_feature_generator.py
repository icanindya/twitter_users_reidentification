import time
import sys
import csv
import os

import emoji
import language_check
import nltk
import numpy as np
import readability
from empath import Empath
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.tokenize.casual import TweetTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import helper
helper.set_csv_field_size_limit()

ALL_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\all_tweets.csv'
YEARLY_TWEETS_PATH = r'D:\Data\Linkage\FL\FL18\ml_datasets\yearly_tweets.csv'

ACRONYMS_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\acronyms.txt'
FUNCTION_WORDS_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\function_words.txt'
PROFANITY_ALVAREZ_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_alvarez.txt"
PROFANITY_ARR_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_arr_bad.txt"
PROFANITY_BANNED_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_banned.txt"
PROFANITY_RACIST_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_racist.txt"
PROFANITY_ZAC_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_zac_anger.txt"
SLANGS_PEEVISH_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\slangs_peevish.txt'


class FeatureExtractor:
    tweet_tokenizer = helper.CustomTweetTokenizer(preserve_case=True, reduce_len=False,
                                                  strip_handles=False, convert_urls=True)

    punctuation_list = {'.', ',', '?', '!', '\'', '"', ':', ';', '-', '–'}
    special_list = {'`', '~', '@', '#', '$', '%', '^', '&', '+', '*', '/', '=',
                    '>', '<', '(', ')', '{', '}', '[', ']', '|', '\\'}

    acronyms = {x.strip() for x in open(ACRONYMS_FILE_PATH).readlines()}
    function_words = {x.strip() for x in open(FUNCTION_WORDS_FILE_PATH).readlines()}
    profanity_alvarez = {x.strip() for x in open(PROFANITY_ALVAREZ_FILE_PATH).readlines()}
    profanity_arr = {x.strip() for x in open(PROFANITY_ARR_FILE_PATH).readlines()}
    profanity_banned = {x.strip() for x in open(PROFANITY_BANNED_FILE_PATH).readlines()}
    profanity_racist = {x.strip() for x in open(PROFANITY_RACIST_FILE_PATH).readlines()}
    profanity_zac = {x.strip() for x in open(PROFANITY_ZAC_FILE_PATH).readlines()}

    profanity_list = profanity_alvarez | profanity_arr | profanity_banned | profanity_racist | profanity_zac
    slangs_list = {x.strip() for x in open(SLANGS_PEEVISH_FILE_PATH).readlines()}

    stopwords = set(stopwords.words('english'))
    articles = {'a', 'an', 'the'}

    noun_tags = {'NN', 'NNS'}
    pronoun_tags = {'PRP', 'PRP$'}
    proper_noun_tags = {'NNP', 'NNPS'}
    verb_tags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    adjective_tags = {'JJ', 'JJR', 'JJS'}
    adverb_tags = {'RB', 'RBR', 'RBS'}
    preposition_tags = {'IN'}
    conjunction_tags = {'CC'}
    interjection_tags = {'UH'}

    # empath_lexicon = Empath()
    # lang_tool = language_check.LanguageTool('en-US')
    sentiment_analzer = SentimentIntensityAnalyzer()

    def __init__(self, tweet_attributes):

        self.num_tweets = tweet_attributes['num_tweets']
        self.num_hashtags = tweet_attributes['num_hashtags']
        self.num_mentions = tweet_attributes['num_mentions']
        self.num_urls = tweet_attributes['num_urls']
        self.num_media = tweet_attributes['num_media']
        self.num_symbols = tweet_attributes['num_symbols']
        self.num_polls = tweet_attributes['num_polls']
        self.text = tweet_attributes['text']
        self.tokens = tweet_attributes['tokens']

        self.token_lengths = [len(token) for token in self.tokens]
        self.tokens_lower = [token.lower() for token in self.tokens]
        self.pos_tags = nltk.pos_tag(self.tokens)
        self.sentences = sent_tokenize(self.text)
        self.num_emojis = emoji.core.emoji_count(self.text)
        self.norm_neg_senti, self.norm_neu_senti, self.norm_pos_senti, self.norm_com_senti = self.normalized_sentiment_values()

        try:
            self.readability_measures = readability.getmeasures(self.tokens, lang='en')
        except:
            self.readability_measures = readability.getmeasures(self.tokens + ['a'], lang='en')

        self.make_char_wise_pass()
        self.make_pos_tag_wise_pass()
        self.make_token_wise_pass()
        self.make_sliding_window_pass()

        self.num_errors = 0
        # lang_error = True
        # while lang_error:
        #     try:
        #         self.num_errors = len(self.lang_tool.check(self.text))
        #         lang_error = False
        #     except:
        #         self.lang_tool = language_check.LanguageTool('en-US')
        #         time.sleep(5)

    def normalized_sentiment_values(self):

        neg_val = neu_val = pos_val = com_val = 0

        for sentence in self.sentences:
            sentiment_values = self.sentiment_analzer.polarity_scores(sentence)
            #            print(sentiment_values)
            neg_val += sentiment_values['neg']
            neu_val += sentiment_values['neu']
            pos_val += sentiment_values['pos']
            com_val += sentiment_values['compound']

        tot_val = neg_val + neu_val + pos_val + com_val

        if tot_val == 0:
            tot_val = 1

        return neg_val / tot_val, neu_val / tot_val, pos_val / tot_val, com_val / tot_val

    def make_char_wise_pass(self):

        self.num_alphas = 0
        self.num_uppers = 0
        self.num_digits = 0
        self.num_whitespaces = 0
        self.num_tabs = 0
        self.num_lines = 0
        self.num_punctuations = 0
        self.num_spacials = 0

        for c in self.text:
            if c.isalpha():
                self.num_alphas += 1
                if c.isupper():
                    self.num_uppers += 1
            elif c.isdigit():
                self.num_digits += 1
            elif c.isspace():
                self.num_whitespaces += 1
                if c == '\t':
                    self.num_tabs += 1
                elif c == '\n':
                    self.num_lines += 1
            elif c in self.punctuation_list:
                self.num_punctuations += 1
            elif c in self.special_list:
                self.num_spacials += 1

    def make_pos_tag_wise_pass(self):

        self.num_nouns = 0
        self.num_pronouns = 0
        self.num_proper_nouns = 0
        self.num_verbs = 0
        self.num_adjectives = 0
        self.num_adverbs = 0
        self.num_prepositions = 0
        self.num_conjunctions = 0
        self.num_interjections = 0

        for word, tag in self.pos_tags:
            if tag in self.noun_tags:
                self.num_nouns += 1
            elif tag in self.pronoun_tags:
                self.num_pronouns += 1
            elif tag in self.proper_noun_tags:
                self.num_proper_nouns += 1
            elif tag in self.verb_tags:
                self.num_verbs += 1
            elif tag in self.adjective_tags:
                self.num_adjectives += 1
            elif tag in self.adverb_tags:
                self.num_adverbs += 1
            elif tag in self.preposition_tags:
                self.num_prepositions += 1
            elif tag in self.conjunction_tags:
                self.num_conjunctions += 1
            elif tag in self.interjection_tags:
                self.num_interjections += 1

    def make_token_wise_pass(self):

        self.token_set = set()
        self.num_small_tokens = 0
        self.num_capital_first_tokens = 0
        self.num_all_capital_tokens = 0
        self.num_stopwords = 0
        self.num_articles = 0

        for token in self.tokens:
            self.token_set.add(token)
            token_len = len(token)

            if token_len < 4:
                self.num_small_tokens += 1

            if ord(token[0]) in range(65, 91):
                self.num_capital_first_tokens += 1
                if all([ord(c) in range(65, 91) for c in token]):
                    self.num_all_capital_tokens += 1

            if token.lower() in self.stopwords:
                self.num_stopwords += 1
                if token.lower() in self.articles:
                    self.num_articles += 1

    def make_sliding_window_pass(self):

        self.num_slangs = 0

        for l in range(1, 6):
            for i in range(0, len(self.tokens_lower) - l + 1):
                phrase = ' '.join(self.tokens_lower[i:i + l])
                if phrase in self.slangs_list:
                    self.num_slangs += 1

    def norm_num_chars(self):

        return len(self.text) / self.num_tweets

    def norm_num_alphas(self):

        return self.num_alphas / len(self.text)

    def norm_num_uppers(self):

        return self.num_uppers / len(self.text)

    def norm_num_digits(self):

        return self.num_digits / len(self.text)

    def norm_num_whitespaces(self):

        return self.num_whitespaces / len(self.text)

    def norm_num_tabs(self):

        return self.num_tabs / len(self.text)

    def norm_num_punctuations(self):

        return self.num_punctuations / len(self.text)

    def norm_num_specials(self):

        return self.num_spacials / len(self.text)

    def norm_num_nouns(self):

        return self.num_nouns / len(self.pos_tags)

    def norm_num_pronouns(self):

        return self.num_pronouns / len(self.pos_tags)

    def norm_num_proper_nouns(self):

        return self.num_proper_nouns / len(self.pos_tags)

    def norm_num_verbs(self):

        return self.num_verbs / len(self.pos_tags)

    def norm_num_adjectives(self):

        return self.num_adjectives / len(self.pos_tags)

    def norm_num_adverbs(self):

        return self.num_adverbs / len(self.pos_tags)

    def norm_num_prepositions(self):

        return self.num_prepositions / len(self.pos_tags)

    def norm_num_conjunctions(self):

        return self.num_conjunctions / len(self.pos_tags)

    def norm_num_interjections(self):

        return self.num_interjections / len(self.pos_tags)

    def norm_num_tokens(self):

        return len(self.tokens) / self.num_tweets

    def norm_num_small_tokens(self):

        return self.num_small_tokens / len(self.tokens)

    def norm_num_unique_tokens(self):

        return len(self.token_set) / len(self.tokens)

    def mean_token_length(self):

        return np.mean(self.token_lengths)

    def std_token_length(self):

        return np.std(self.token_lengths)

    def min_token_length(self):

        return min(self.token_lengths)

    def max_token_length(self):

        return max(self.token_lengths)

    def norm_num_capital_first_tokens(self):

        return self.num_capital_first_tokens / len(self.tokens)

    def norm_num_all_capital_tokens(self):

        return self.num_all_capital_tokens / len(self.tokens)

    def norm_num_stopwords(self):

        return self.num_stopwords / len(self.tokens)

    def norm_num_articles(self):

        return self.num_articles / len(self.tokens)

    def norm_num_sentences(self):

        return len(self.sentences) / self.num_tweets

    def norm_num_acronyms(self):

        return len([item for item in self.tokens if item in self.acronyms])

    def kincaid_readability(self):

        return self.readability_measures['readability grades']['Kincaid']

    def ari_readability(self):

        return self.readability_measures['readability grades']['ARI']

    def colemanliau_readability(self):

        return self.readability_measures['readability grades']['Coleman-Liau']

    def flesch_readability(self):

        return self.readability_measures['readability grades']['FleschReadingEase']

    def gunningfog_readability(self):

        return self.readability_measures['readability grades']['GunningFogIndex']

    def lix_readability(self):

        return self.readability_measures['readability grades']['LIX']

    def smog_readability(self):

        return self.readability_measures['readability grades']['SMOGIndex']

    def rix_readability(self):

        return self.readability_measures['readability grades']['RIX']

    def dalechall_readability(self):

        return self.readability_measures['readability grades']['DaleChallIndex']

    def mean_chars_per_word(self):

        return self.readability_measures['sentence info']['characters_per_word']

    def mean_syllables_per_word(self):

        return self.readability_measures['sentence info']['syll_per_word']

    def type_token_ratio(self):

        return self.readability_measures['sentence info']['type_token_ratio']

    def norm_num_wordtypes(self):

        return self.readability_measures['sentence info']['wordtypes'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_long_words(self):

        return self.readability_measures['sentence info']['long_words'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_complex_words(self):

        return self.readability_measures['sentence info']['complex_words'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_complex_words_dc(self):

        return self.readability_measures['sentence info']['complex_words_dc'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_tobeverbs(self):

        return self.readability_measures['word usage']['tobeverb'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_auxverbs(self):

        return self.readability_measures['word usage']['auxverb'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_nominalization(self):

        return self.readability_measures['word usage']['nominalization'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_interrogative(self):

        return self.readability_measures['sentence beginnings']['interrogative'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_subordination(self):

        return self.readability_measures['sentence beginnings']['subordination'] /\
               self.readability_measures['sentence info']['words']

    def norm_num_hashtags(self):

        return self.num_hashtags / self.num_tweets

    def norm_num_mentions(self):

        return self.num_mentions / self.num_tweets

    def norm_num_urls(self):

        return self.num_urls / self.num_tweets

    def norm_num_media(self):

        return self.num_media / self.num_tweets

    def norm_num_symbols(self):

        return self.num_symbols / self.num_tweets

    def norm_num_polls(self):

        return self.num_polls / self.num_tweets

    def norm_num_lines(self):

        return self.num_lines / self.num_tweets

    def norm_num_emojis(self):

        return self.num_emojis / self.num_tweets

    def norm_num_slangs(self):

        return self.num_slangs / self.num_tweets

    def norm_num_errors(self):

        return self.num_errors / self.num_tweets

    # def normalized_empath_values(self):
    #     self.empath_features = self.empath_lexicon.analyze(self.text, normalize=False)
    #
    #     return [v / len(self.tweets) for v in self.empath_features.values()]

    def get_all_features(self):

        features = [self.norm_num_chars(),
                    self.norm_num_alphas(),
                    self.norm_num_uppers(),
                    self.norm_num_digits(),
                    self.norm_num_whitespaces(),
                    self.norm_num_tabs(),
                    self.norm_num_punctuations(),
                    self.norm_num_specials(),
                    self.norm_num_nouns(),
                    self.norm_num_pronouns(),
                    self.norm_num_proper_nouns(),
                    self.norm_num_verbs(),
                    self.norm_num_adjectives(),
                    self.norm_num_adverbs(),
                    self.norm_num_prepositions(),
                    self.norm_num_conjunctions(),
                    self.norm_num_interjections(),
                    self.norm_num_tokens(),
                    self.norm_num_small_tokens(),
                    self.norm_num_unique_tokens(),
                    self.mean_token_length(),
                    self.std_token_length(),
                    self.min_token_length(),
                    self.max_token_length(),
                    self.norm_num_capital_first_tokens(),
                    self.norm_num_all_capital_tokens(),
                    self.norm_num_stopwords(),
                    self.norm_num_articles(),
                    self.norm_num_sentences(),
                    self.norm_num_acronyms(),
                    self.kincaid_readability(),
                    self.ari_readability(),
                    self.colemanliau_readability(),
                    self.flesch_readability(),
                    self.gunningfog_readability(),
                    self.lix_readability(),
                    self.smog_readability(),
                    self.rix_readability(),
                    self.dalechall_readability(),
                    self.mean_chars_per_word(),
                    self.mean_syllables_per_word(),
                    self.type_token_ratio(),
                    self.norm_num_wordtypes(),
                    self.norm_num_long_words(),
                    self.norm_num_complex_words(),
                    self.norm_num_complex_words_dc(),
                    self.norm_num_tobeverbs(),
                    self.norm_num_auxverbs(),
                    self.norm_num_nominalization(),
                    self.norm_num_interrogative(),
                    self.norm_num_subordination(),
                    self.norm_num_hashtags(),
                    self.norm_num_mentions(),
                    self.norm_num_urls(),
                    self.norm_num_media(),
                    self.norm_num_symbols(),
                    self.norm_num_polls(),
                    self.norm_num_lines(),
                    self.norm_num_emojis(),
                    self.norm_num_slangs(),
                    self.norm_neg_senti,
                    self.norm_neu_senti,
                    self.norm_pos_senti,
                    self.norm_com_senti]

        return features


def vectorize_docs(dataset_path, tokens_path, features_path):

    start = time.time()

    with open(features_path, 'w', newline='', encoding='utf-8') as wf:
        csv_writer = csv.writer(wf, delimiter=',')
        feature_names = ['norm_num_chars', 'norm_num_alphas', 'norm_num_uppers',
                         'norm_num_digits', 'norm_num_whitespaces', 'norm_num_tabs',
                         'norm_num_punctuations', 'norm_num_specials',
                         'norm_num_nouns', 'norm_num_pronouns',
                         'norm_num_proper_nouns', 'norm_num_verbs',
                         'norm_num_adjectives', 'norm_num_adverbs',
                         'norm_num_prepositions', 'norm_num_conjunctions',
                         'norm_num_interjections', 'norm_num_tokens',
                         'norm_num_small_tokens', 'norm_num_unique_tokens',
                         'mean_token_length', 'std_token_length',
                         'min_token_length', 'max_token_length',
                         'norm_num_capital_first_tokens',
                         'norm_num_all_capital_tokens',
                         'norm_num_stopwords', 'norm_num_articles',
                         'norm_num_sentences', 'norm_num_acronyms',
                         'kincaid_readability', 'ari_readability',
                         'colemanliau_readability', 'flesch_readability',
                         'gunningfog_readability', 'lix_readability',
                         'smog_readability', 'rix_readability',
                         'dalechall_readability', 'mean_chars_per_word',
                         'mean_syllables_per_word', 'type_token_ratio',
                         'norm_num_wordtypes', 'norm_num_long_words',
                         'norm_num_complex_words', 'norm_num_complex_words_dc',
                         'norm_num_tobeverbs', 'norm_num_auxverbs',
                         'norm_num_nominalization', 'norm_num_interrogative',
                         'norm_num_subordination', 'norm_num_hashtags',
                         'norm_num_mentions', 'norm_num_urls', 'norm_num_media',
                         'norm_num_symbols', 'norm_num_polls', 'norm_num_lines',
                         'norm_num_emojis', 'norm_num_slangs', 'norm_neg_senti',
                         'norm_neu_senti', 'norm_pos_senti', 'norm_com_senti']
        csv_writer.writerow(feature_names)

        with open(dataset_path, 'r', encoding='utf-8') as rf1:
            csv_reader1 = csv.DictReader(rf1, delimiter=',')
            with open(tokens_path, 'r', encoding='utf-8') as rf2:
                csv_reader2 = csv.DictReader(rf2, delimiter=',')

                for i, row1 in enumerate(csv_reader1):
                    row2 = next(csv_reader2)
                    if i % 100 == 0:
                        print('write csv row', i)

                    tweet_attributes = {'num_tweets': int(row1['num_tweets']),
                                        'num_hashtags': int(row1['num_hashtags']),
                                        'num_mentions': int(row1['num_mentions']),
                                        'num_urls': int(row1['num_urls']),
                                        'num_media': int(row1['num_media']),
                                        'num_symbols': int(row1['num_symbols']),
                                        'num_polls': int(row1['num_polls']),
                                        'text': row1['text'],
                                        'tokens': row2['tokens_joined'].split()}

                    feature_vector = [str(x) for x in FeatureExtractor(tweet_attributes).get_all_features()]
                    csv_writer.writerow(feature_vector)

    end = time.time()

    print('total records: {}, time: {}'.format(i + 1, (end - start)))


if __name__ == '__main__':

    option = sys.argv[1]

    if option == '1':
        dataset_path = ALL_TWEETS_PATH

    elif option == '2':
        dataset_path = YEARLY_TWEETS_PATH

    file_name, file_ext = os.path.splitext(dataset_path)
    tokens_path = file_name + '_tokens.csv'

    features_path = file_name + '_linguistic_features.csv'
    vectorize_docs(dataset_path, tokens_path, features_path)
