import emoji

from nltk.tokenize.stanford import StanfordTokenizer

s = "Good muffins :-X cost $3.88\nin New York.  Please buy me\ntwo of them.\nThanks."
tokens = StanfordTokenizer().tokenize(s)

print(tokens)


a = {'a', 'b', 'c'}
b = {'b', 'c', 'd'}
c = {'a', 'd', 'e'}

d = a | b | c


print(d)
