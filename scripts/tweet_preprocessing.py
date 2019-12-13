from urllib.parse import urlparse
import re


    text = re.sub('https?:\/\/\S+|www\.(\w+\.)+\S*', '<URL>', text)
   print(preprocess('this is https://www.yahoo.com this is b-: :p this is <3 +764957 @dtrump :( :-(( :*'))