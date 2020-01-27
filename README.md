# Re-identification of Twitter Users Using Prediction-based Record Linkage
This project aims to reveal the the real identities of Twitter users using US Voter Registration Records.

## Summary

In this project, I try to find the real world identities of Twitter users. At first, by exploiting a data leakage vulnerability in Twitter web interface I collect the real identities of 200K Twitter users and track them in US voter registration data. Then using the content and network information of these users, I build ML/NLP models to predict personal attributes (age-group, sex, race, party affiliation, location). Then using these predicted attributes along with Twitter name and handle, I link an unknown Twitter user with his/her voter registration entry using probabilistic record linkage models. Thus I find many sensitive information e.g., phone number, address, email address, family members etc. about the user. 

## Methodology
As of July 2019, Twitter gives an user the ability to import his email contacts book and see the corresponding Twitter profiles which registered using that email addresses in the contacts book, provided that the profiles give consent of finding them via email address. This seemingly innocuous feature can be exploited to enumerate the Twitter profiles corresponding to a database of millions of email address. We develop a framework to efficiently 

However, for many peoples' email addresses may not be available in the database. 

Latnya Sweeny showed that 87% of US population could be uniquely identifies based on their DoB, Sex & ZIP code. Inspired by that idea, here we would like to predict age, sex, race, political afficiliation and city information and use those predicted attributes to re-identify a Twitter user.

## Data Collection

**The following data leakage vulnerability was exclusively available in Twitter Web interface (as of July 2019). Twitter does not provide API for collecting this kind of information.**

Using Selenium automation library, email addresses from Florida Voter Records are uploaded to email contact list one at a time and then Twitter is asked to import the contact list using OAuth. If the voter with the email address has a Twitter account and gives consent to find him by email address then Twitter shows the corresponding Twitter account. Some optimizations are done and 200K Twitter users are linked.

* For voters of Florida we have-

  - First Name, Middle Name, Age, Gender, Race, Party, City, Email
  - Sensitive attributes

* For Twitter users we have-

  - Twitter Name, Twitter Handle, Tweets, Followers, Following, Email
  - Tweets from direct followers and friends
  
* The total data size is more than 500 GB in MongoDB
  

## Attribute Prediction
Used the following models-

* Extracted 64 NLP Features
* Doc2Vec, fastText, GloVe features
* LDA topic modeling features
* VDCNN - Very Deep Convolutional Neural Network
* HAN - Hierarchical Attention Network

## Record Linkage
We apply a probabilistic linkage mechnism similar to Fellegi-Sunter Expectation Maximization mechanism.


