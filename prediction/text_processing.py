import time
from collections import defaultdict

import emojis
import language_check
import nltk
import numpy as np
import readability
from empath import Empath
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.tokenize.casual import TweetTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ACRONYMS_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\acronyms.txt'
FUNCTION_WORDS_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\function_words.txt'
PROFANITY_ALVAREZ_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\function_words.txt"
PROFANITY_ARR_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_arr_bad.txt"
PROFANITY_BANNED_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_banned.txt"
PROFANITY_RACIST_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_racist.txt"
PROFANITY_ZAC_FILE_PATH = r"D:\Data\Linkage\FL\FL18\lexicons\trinker-lexicon-4c5e22b\data_txt\profanity_zac_anger.txt"
SLANGS_PEEVISH_FILE_PATH = r'D:\Data\Linkage\FL\FL18\lexicons\slangs_peevish.txt'


class FeatureExtractor:
    tweet_tokenizer = TweetTokenizer(preserve_case=True, reduce_len=False, strip_handles=False)

    punctuation_list = ['.', ',', '?', '!', '\'', '"', ':', ';', '-', '–']
    special_list = ['`', '~', '@', '#', '$', '%', '^', '&', '+', '*', '/', '=', '>', '<', '(', ')', '{', '}', '[', ']',
                    '|', '\\']

    acronyms = list(set([x.strip() for x in open(ACRONYMS_FILE_PATH).readlines()]))
    function_words = list(set([x.strip() for x in open(FUNCTION_WORDS_FILE_PATH).readlines()]))
    profanity_alvarez = [x.strip() for x in open(PROFANITY_ALVAREZ_FILE_PATH).readlines()]
    profanity_arr = [x.strip() for x in open(PROFANITY_ARR_FILE_PATH).readlines()]
    profanity_banned = [x.strip() for x in open(PROFANITY_BANNED_FILE_PATH).readlines()]
    profanity_racist = [x.strip() for x in open(PROFANITY_RACIST_FILE_PATH).readlines()]
    profanity_zac = [x.strip() for x in open(PROFANITY_ZAC_FILE_PATH).readlines()]

    profanity_list = list(set(profanity_alvarez + profanity_arr + profanity_banned + profanity_racist + profanity_zac))
    slangs_list = [x.strip() for x in open(SLANGS_PEEVISH_FILE_PATH).readlines()]

    stopwords = set(stopwords.words('english'))
    articles = ['a', 'an', 'the']

    noun_tags = ['NN', 'NNS']
    pronoun_tags = ['PRP', 'PRP$']
    proper_noun_tags = ['NNP', 'NNPS']
    verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adjective_tags = ['JJ', 'JJR', 'JJS']
    adverb_tags = ['RB', 'RBR', 'RBS']
    preposition_tags = ['IN']
    conjunction_tags = ['CC']
    interjection_tags = ['UH']

    empath_lexicon = Empath()
    lang_tool = language_check.LanguageTool('en-US')
    sentiment_analzer = SentimentIntensityAnalyzer()

    def __init__(self, tweets, tweets_data):
        self.tweets = tweets
        self.text = ' '.join(tweets)
        self.num_hashtags = tweets_data['num_hashtags']
        self.num_mentions = tweets_data['num_mentions']
        self.num_urls = tweets_data['num_urls']
        self.num_media = tweets_data['num_media']
        self.num_symbols = tweets_data['num_symbols']
        self.num_polls = tweets_data['num_polls']
        self.tokens = self.tweet_tokenizer.tokenize(self.text)
        self.token_lengths = [len(token) for token in self.tokens]
        self.tokens_lower = [token.lower() for token in self.tokens]
        self.pos_tags = nltk.pos_tag(self.tokens)
        self.num_emojis = emojis.count(self.text)
        self.empath_features = self.empath_lexicon.analyze(self.text, normalize=False)

        try:
            self.readability_measures = readability.getmeasures(self.tokens, lang='en')
        except:
            self.readability_measures = readability.getmeasures(self.tokens + ['a'], lang='en')

        lang_error = True
        while lang_error:
            try:
                self.num_errors = len(self.lang_tool.check(self.text))
                lang_error = False
            except:
                self.lang_tool = language_check.LanguageTool('en-US')
                time.sleep(5)

        self.make_tweet_wise_pass()
        self.make_char_wise_pass()
        self.make_pos_tag_wise_pass()
        self.make_token_wise_pass()
        self.make_sliding_window_pass()

    def make_tweet_wise_pass(self):

        self.sentences = []

        for tweet in self.tweets:
            self.sentences.extend(sent_tokenize(tweet))

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
                    #                    print(phrase)
                    self.num_slangs += 1

    def num_normalized_chars(self):

        return len(self.text) / len(self.tweets)

    def num_normalized_alphas(self):

        return self.num_alphas / len(self.text)

    def num_normalized_uppers(self):

        return self.num_uppers / len(self.text)

    def num_normalized_digits(self):

        return self.num_digits / len(self.text)

    def num_normalized_whitespaces(self):

        return self.num_whitespaces / len(self.text)

    def num_normalized_tabs(self):

        return self.num_tabs / len(self.text)

    def num_normalized_punctuations(self):

        return self.num_punctuations / len(self.text)

    def num_normalized_specials(self):

        return self.num_spacials / len(self.text)

    def num_normalized_nouns(self):

        return self.num_nouns / len(self.pos_tags)

    def num_normalized_pronouns(self):

        return self.num_pronouns / len(self.pos_tags)

    def num_normalized_proper_nouns(self):

        return self.num_proper_nouns / len(self.pos_tags)

    def num_normalized_verbs(self):

        return self.num_verbs / len(self.pos_tags)

    def num_normalized_adjectives(self):

        return self.num_adjectives / len(self.pos_tags)

    def num_normalized_adverbs(self):

        return self.num_adverbs / len(self.pos_tags)

    def num_normalized_prepositions(self):

        return self.num_prepositions / len(self.pos_tags)

    def num_normalized_conjunctions(self):

        return self.num_conjunctions / len(self.pos_tags)

    def num_normalized_interjections(self):

        return self.num_interjections / len(self.pos_tags)

    def num_normalized_tokens(self):

        return len(self.tokens) / len(self.tweets)

    def num_normalized_small_tokens(self):

        return self.num_small_tokens / len(self.tokens)

    def num_normalized_unique_tokens(self):

        return len(self.token_set) / len(self.tokens)

    def mean_token_length(self):

        return np.mean(self.token_lengths)

    def std_token_length(self):

        return np.std(self.token_lengths)

    def min_token_length(self):

        return min(self.token_lengths)

    def max_token_length(self):

        return max(self.token_lengths)

    def num_normalized_capital_first_tokens(self):

        return self.num_capital_first_tokens / len(self.tokens)

    def num_normalized_all_capital_tokens(self):

        return self.num_all_capital_tokens / len(self.tokens)

    def num_normalized_stopwords(self):

        return self.num_stopwords / len(self.tokens)

    def num_normalized_articles(self):

        return self.num_articles / len(self.tokens)

    def num_normalized_sentences(self):

        return len(self.sentences) / len(self.tweets)

    def mean_chars_per_sentence(self):

        return sum([len(sentence) for sentence in self.sentences]) / len(self.sentences)

    def mean_tokens_per_sentence(self):

        return sum([len(self.tweet_tokenizer.tokenize(sentence)) for sentence in self.sentences]) / len(self.sentences)

    def num_normalized_acronyms(self):

        return len([item for item in self.tokens if item in self.acronyms])

    def kincaid_readability_score(self):

        return self.readability_measures['readability grades']['Kincaid']

    def ari_readability_score(self):

        return self.readability_measures['readability grades']['ARI']

    def colemanliau_readability_score(self):

        return self.readability_measures['readability grades']['Coleman-Liau']

    def flesch_readability_score(self):

        return self.readability_measures['readability grades']['FleschReadingEase']

    def gunningfog_readability_score(self):

        return self.readability_measures['readability grades']['GunningFogIndex']

    def lix_readability_score(self):

        return self.readability_measures['readability grades']['LIX']

    def smog_readability_score(self):

        return self.readability_measures['readability grades']['SMOGIndex']

    def rix_readability_score(self):

        return self.readability_measures['readability grades']['RIX']

    def dalechall_readability_score(self):

        return self.readability_measures['readability grades']['DaleChallIndex']

    def mean_chars_per_word(self):

        return self.readability_measures['sentence info']['characters_per_word']

    def mean_syllables_per_word(self):

        return self.readability_measures['sentence info']['syll_per_word']

    def mean_words_per_sentence(self):

        return self.readability_measures['sentence info']['words_per_sentence']

    def mean_sentences_per_paragraph(self):

        return self.readability_measures['sentence info']['sentences_per_paragraph']

    def type_token_ratio(self):

        return self.readability_measures['sentence info']['type_token_ratio']

    def num_normalized_wordtypes(self):

        return self.readability_measures['sentence info']['wordtypes'] / self.readability_measures['sentence info'][
            'words']

    def num_normalized_long_words(self):

        return self.readability_measures['sentence info']['long_words'] / self.readability_measures['sentence info'][
            'words']

    def num_normalized_complex_words(self):

        return self.readability_measures['sentence info']['complex_words'] / self.readability_measures['sentence info'][
            'words']

    def num_normalized_complex_words_dc(self):

        return self.readability_measures['sentence info']['complex_words_dc'] / \
               self.readability_measures['sentence info']['words']

    def num_normalized_tobeverbs(self):

        return self.readability_measures['word usage']['tobeverb'] / self.readability_measures['sentence info']['words']

    def num_normalized_auxverbs(self):

        return self.readability_measures['word usage']['auxverb'] / self.readability_measures['sentence info']['words']

    def num_normalized_nominalization(self):

        return self.readability_measures['word usage']['nominalization'] / self.readability_measures['sentence info'][
            'words']

    def num_normalized_interrogative(self):

        return self.readability_measures['sentence beginnings']['interrogative'] / \
               self.readability_measures['sentence info']['words']

    def num_normalized_subordination(self):

        return self.readability_measures['sentence beginnings']['subordination'] / \
               self.readability_measures['sentence info']['words']

    def num_normalized_hashtags(self):

        return self.num_hashtags / len(self.tweets)

    def num_normalized_mentions(self):

        return self.num_mentions / len(self.tweets)

    def num_normalized_urls(self):

        return self.num_urls / len(self.tweets)

    def num_normalized_media(self):

        return self.num_media / len(self.tweets)

    def num_normalized_symbols(self):

        return self.num_symbols / len(self.tweets)

    def num_normalized_polls(self):

        return self.num_polls / len(self.tweets)

    def num_normalized_lines(self):

        return self.num_lines / len(self.tweets)

    def num_normalized_emojis(self):

        return self.num_emojis / len(self.tweets)

    def num_normalized_slangs(self):

        return self.num_slangs / len(self.tweets)

    def num_normalized_errors(self):

        return self.num_errors / len(self.tweets)

    def normalized_empath_values(self):

        return [v / len(self.tweets) for v in self.empath_features.values()]

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

        return [neg_val / tot_val, neu_val / tot_val, pos_val / tot_val, com_val / tot_val]

    def get_all_features(self):

        features = [self.num_normalized_chars(),
                    self.num_normalized_alphas(),
                    self.num_normalized_uppers(),
                    self.num_normalized_digits(),
                    self.num_normalized_whitespaces(),
                    self.num_normalized_tabs(),
                    self.num_normalized_punctuations(),
                    self.num_normalized_specials(),
                    self.num_normalized_nouns(),
                    self.num_normalized_pronouns(),
                    self.num_normalized_proper_nouns(),
                    self.num_normalized_verbs(),
                    self.num_normalized_adjectives(),
                    self.num_normalized_adverbs(),
                    self.num_normalized_prepositions(),
                    self.num_normalized_conjunctions(),
                    self.num_normalized_interjections(),
                    self.num_normalized_tokens(),
                    self.num_normalized_small_tokens(),
                    self.num_normalized_unique_tokens(),
                    self.mean_token_length(),
                    self.std_token_length(),
                    self.min_token_length(),
                    self.max_token_length(),
                    self.num_normalized_capital_first_tokens(),
                    self.num_normalized_all_capital_tokens(),
                    self.num_normalized_stopwords(),
                    self.num_normalized_articles(),
                    self.num_normalized_sentences(),
                    self.mean_chars_per_sentence(),
                    self.mean_tokens_per_sentence(),
                    self.num_normalized_acronyms(),
                    self.kincaid_readability_score(),
                    self.ari_readability_score(),
                    self.colemanliau_readability_score(),
                    self.flesch_readability_score(),
                    self.gunningfog_readability_score(),
                    self.lix_readability_score(),
                    self.smog_readability_score(),
                    self.rix_readability_score(),
                    self.dalechall_readability_score(),
                    self.mean_chars_per_word(),
                    self.mean_syllables_per_word(),
                    self.mean_words_per_sentence(),
                    self.mean_sentences_per_paragraph(),
                    self.type_token_ratio(),
                    self.num_normalized_wordtypes(),
                    self.num_normalized_long_words(),
                    self.num_normalized_complex_words(),
                    self.num_normalized_complex_words_dc(),
                    self.num_normalized_tobeverbs(),
                    self.num_normalized_auxverbs(),
                    self.num_normalized_nominalization(),
                    self.num_normalized_interrogative(),
                    self.num_normalized_subordination(),
                    self.num_normalized_hashtags(),
                    self.num_normalized_mentions(),
                    self.num_normalized_urls(),
                    self.num_normalized_media(),
                    self.num_normalized_symbols(),
                    self.num_normalized_polls(),
                    self.num_normalized_lines(),
                    self.num_normalized_emojis(),
                    self.num_normalized_slangs(),
                    self.num_normalized_errors()]
        features.extend(self.normalized_empath_values())
        features.extend(self.normalized_sentiment_values())
        return features


if __name__ == '__main__':
    tweets_data = defaultdict()
    tweets_data['num_hashtags'] = 0
    tweets_data['num_mentions'] = 0
    tweets_data['num_urls'] = 0
    tweets_data['num_media'] = 0
    tweets_data['num_symbols'] = 0
    tweets_data['num_polls'] = 0

    fe = FeatureExtractor([''], tweets_data)
    print(fe.readability_measures)
