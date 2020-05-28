# Asssessing the Re-identification Risk of Twitter Users on US Voter Records
This project aims to reveal the real identities of Twitter users using US Voter Registration Records.

## Methodology

Traditional re-identification attacks depend on already documented attributes in structured data. In this work, we introduce a novel approach to utilize the attributes predicted from unstructured data using machine learning to link offline data sources with online profiles.

At first by exploiting a data leakage vulnerability in Twitter web interface, 200K Twitter users are tracked in US Voter Registration data, which contains their real identities and personal attributes. Using the content and network information i.e., tweets, friends, followers etc. of these users, ML/NLP models are built to predict some of the personal attributes specifically age-group, sex, race, party affiliation and city. Finally, by utilizing these predicted attributes along with display name and handle, an unknown Twitter user is linked with his voter registration entry using deterministic/probabilistic record linkage models. Each linkage "match" reveals some sensitive information e.g., phone number, address, email address, family members etc. of a Twitter user. 

## Ground Truth Collection

As of July 2019, Twitter had a feature that would let an user to import his contact list from an email service and view the corresponding Twitter profiles which registered using some email address in the list. However, Twitter didn't have an API support to access this feature possibly in order to prevent abuse. On top of that, the process was time consuming and could not be easily automated using simple web scraping technique because of an OAuth workflow that would allow Twitter to aquire permission of importing the contact list from the email service. Hence, we develop an automation framework using Selenium to do this task efficiently. Using our framework this seemingly innocuous feature can be exploited to enumerate the Twitter profiles corresponding to a database of millions of email addresses. We upload 1M email addresses from FL voter records and some 200K Twitter users are linked. 

## Data Collection

* Voter registration records of 14M FL voters:

  - first Name, middle Name, last name, DoB, gender, race, party, city, county, ZIP code, email address, phone number

* Content & network information of 200K linked Twitter users:

  - Display name, Twitter handle, tweets and metadata, followers, friends
  - Tweets of direct followers and friends
  
* The total data size is more than 500 GB in MongoDB
  

## Attribute Prediction

* Using Tweets:
  * Word n-grams TF-IDF: top 10K unigrams, top 10K bigrams + Random Forest
  * Lexicon features: [Empath](https://hci.stanford.edu/publications/2016/ethan/empath-chi-2016.pdf) 
  * 64 NLP Features + Neural Net
  * Doc2Vec, fastText, GloVe features + Neural Net
  * LDA topic modeling features + Neural Net
  * VDCNN - Very Deep Convolutional Neural Network ([read more](https://arxiv.org/abs/1606.01781)) 
  * HAN - Hierarchical Attention Network ([read more](https://www.aclweb.org/anthology/N16-1174/))

* Using Twitter name and Handle:
  * n-grams + LSTM
  * n-grams + Temporal Convolution + LSTM 

* Using Network:
  * (to be done)

## Record Linkage

* Several deterministic record linkage models
* Fellegi-Sunter Expectation Maximization model

## Results

* Results have been published in a conference paper, which is currently under review.

## Technologies

This project uses the following technologies:

* Machine Learning: scikit-learn
* NLP: NLTK, Gensim
* Database: MongoDB
* Data Scraping: Selenium, Google API, Twitter API
* Charting: Matplotlib
