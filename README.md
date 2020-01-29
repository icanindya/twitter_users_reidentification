# Re-identification of Twitter Users Using Prediction-based Record Linkage
This project aims to reveal the the real identities of Twitter users using US Voter Registration Records.

## Methodology

At first, by exploiting a data leakage vulnerability in Twitter web interface 200K Twitter users are tracked in US Voter Registration data, which contains their real identities and personal attributes. Using the content and network information i.e., tweets, friends, followers etc. of these users, ML/NLP models are built to predict some of the personal attributes specifically age-group, sex, race, party affiliation and city. Finally, by utilizing these predicted attributes along with display name and handle, an unknown Twitter user is linked with his voter registration entry using probabilistic record linkage models. Each linkage "match" reveals some sensitive information e.g., phone number, address, email address, family members etc. of a Twitter user. 

## Ground Truth Collection

**Note**: *The following data leakage vulnerability was exclusively available in Twitter Web interface till July 2019. Twitter never provided API support for collecting this kind of information.*

Twitter gives an user the ability to import contact list from an email service and show the corresponding Twitter profiles which registered using some email address in the contact list, provided that the profiles give consent of finding them via email address. This seemingly innocuous feature can be exploited to enumerate the Twitter profiles corresponding to a database of millions of email address. We develop an automation framework to do this task efficiently and some 200K Twitter users are linked. 

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


