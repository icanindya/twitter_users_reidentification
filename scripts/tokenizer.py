# from nltk.tokenize import sent_tokenize
#
# text = "New hair selfie:]] finally the color I wanted #cherryred http://t.co/j10E3WIAAi " \
#        "@CharlesTrippy @AlliTrippy I know I'm late to the party on this but 😔 love you both and support your decisions..though it sucks " \
#        "Welp...flight transfer to people that actually love me " \
#        "Oh my flipping fuhhhh I'm pissed off! " \
#        "I am out 600 dollars. Because of you. #really #pissed #wtf " \
#        "I really have no fucking words. #pissedoff #seeingred " \
#        "Every time #happypuppy #dinner #breakfast http://t.co/m2tqU0p7Iq"
# print('\n'.join(sent_tokenize(text)))


eot_tweets = []
tweets = ['a', 'b', 'c', '']

for tweet in tweets:
    if tweet.endswith(('.', ',', '?')) is False:
        eot_tweets.append(tweet + '.')
    else:
        eot_tweets.append(tweet)
print(eot_tweets)