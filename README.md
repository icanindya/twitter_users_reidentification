# Re-identification of Twitter Users Using Prediction-based Record Linkage
This project aims to reveal the real identities of Twitter users using US Voter Registration Records. It analyses which users are at significantly more risk of identity disclosure and what approaches should be taken to mitigate the risk. 

## Techologies

This project uses the following technologies:

* scikit-learn
* MongoDB
* Selenium
* Google API
* Twitter API
* Matplotlib

## Methodology

At first, by exploiting a data leakage vulnerability in Twitter web interface 200K Twitter users are tracked in US Voter Registration data, which contains their real identities and personal attributes. Using the content and network information i.e., tweets, friends, followers etc. of these users, ML/NLP models are built to predict some of the personal attributes specifically age-group, sex, race, party affiliation and city. Finally, by utilizing these predicted attributes along with display name and handle, an unknown Twitter user is linked with his voter registration entry using deterministic/probabilistic record linkage models. Each linkage "match" reveals some sensitive information e.g., phone number, address, email address, family members etc. of a Twitter user. 

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

* Stemmed word n-grams: top 10K unigrams, top 10K bigrams
* 64 NLP Features
* Doc2Vec, fastText, GloVe features
* LDA topic modeling features
* VDCNN - Very Deep Convolutional Neural Network ([read more](https://arxiv.org/abs/1606.01781)) 
* HAN - Hierarchical Attention Network ([read more](https://www.aclweb.org/anthology/N16-1174/))

## Record Linkage

* Several deterministic record linkage models
* Fellegi-Sunter Expectation Maximization model 


