##############################################
# Load Libraries
##############################################

import pandas as pd
from sklearn.externals import joblib
import boto3
import io
from io import StringIO


##############################################
# Load Data
##############################################

s3 = boto3.client('s3')

obj_tweets = s3.get_object(Bucket='trustar-dashboard-twitter', Key='tweets.csv')
obj_avgs = s3.get_object(Bucket='trustar-dashboard-twitter', Key='running_avgs.csv')

df = pd.read_csv(io.BytesIO(obj_tweets['Body'].read()))

df['created']=df['created'].apply(lambda tweet: tweet[:10])

tweet_dates = sorted(df.created.unique())

priors = pd.read_csv(io.BytesIO(obj_avgs['Body'].read()))
last_day = priors.date.max()


##############################################
# Helper Functions
##############################################

import re
def process_text(data):
    '''
    input: Tweet
    Remove hashtags, tags, URLs, special characters. Tokenize.
    '''
    regex_remove_ahu = "([A-Za-z0-9]+_[A-Za-z0-9]+)|(@[A-Za-z0-9]+)|(_[A-Za-z0-9]+)|(#[A-Za-z0-9]+)|(\w+:\/\/\S+)|^RT|http.+?"
    data =  re.sub(regex_remove_ahu, ' ',data)
    regex_remove_punct = "([^0-9A-Za-z \t])"
    data = re.sub(regex_remove_punct, ' ',data)
    return data.split()


from nltk.corpus import wordnet
#import enchant
d = enchant.Dict("en_US")
obj_tech = s3.get_object(Bucket='trustar-dashboard-twitter', Key='tech.csv')
tech_file = pd.read_csv(io.BytesIO(obj_tech['Body'].read()), header=None)
def flagged_words(data):
    '''
    input: Processed tweet
    Given a list of words, return possible Malware names.
    '''
    possible = list(set(data))
    possible = [word for word in possible if word.lower() not in tech_file[0].values]
    possible = [word for word in possible if (len(word)>3 and not(d.check(word.lower())))] 
    possible = [word for word in possible if len(wordnet.synsets(word))==0]
    possible = [word for word in possible if (not word.islower() and not word.isupper())] # Keep CamelCase words
    return possible


def get_context(context, flagged, n=4):
    '''
    Given a processed tweet and a list of flagged word, return context for each flagged word.
    '''
    for index,word in enumerate(context):
        if word in flagged:
            pre = context[index-n:index]
            pos = context[index+1:index+(n+1)]
            yield([word,str(pre+pos)])
            
            
def get_context_df(df):
    df_context = []

    for row in df.iterrows():
        flagged = row[1][-1]
        context = row[1][-2]
        for c in get_context(context, flagged):
            df_context.append(c)
        
    df_context = pd.DataFrame(df_context)
    df_context.columns = ['flagged','context']
    
    return df_context


obj_malware = s3.get_object(Bucket='trustar-dashboard-twitter', Key='known_malware.csv')
malware_file = pd.read_csv(io.BytesIO(obj_malware['Body'].read()), header=None)
malware_file[0] = malware_file[0].apply(lambda m: m.lower())

obj_model = s3.get_object(Bucket='trustar-dashboard-twitter', Key='model.pkl')
model = joblib.load(io.BytesIO(obj_model['Body'].read()))
def get_prediction(df):
    predictions = []
    for row in df.iterrows():
        flagged = row[1]['flagged']
        if flagged.lower() in malware_file[0].values:
            predictions.append(1.0)
        else:
            context = row[1]['context']
            predictions.append(model.predict([context])[0])
    return predictions


def running_avg(df_prior, df_current, flagged):
    df_current = df_current[df_current['flagged']==flagged]
    if flagged.lower() in malware_file[0].values:
        return 1
    elif flagged in df_prior.flagged.values:
        df_prior = df_prior[df_prior['flagged']==flagged]
        df = pd.concat([df_prior,df_current])
        return sum(df.predicted * df.frequency) * 1.0 / sum(df.frequency)
    else:
        return sum(df_current.predicted * df_current.frequency) * 1.0 / sum(df_current.frequency)
        
        
##############################################
# Process
##############################################

for day in tweet_dates[tweet_dates.index(last_day)+1:-2]:
    obj_avgs = s3.get_object(Bucket='trustar-dashboard-twitter', Key='running_avgs.csv')
    priors = pd.read_csv(io.BytesIO(obj_avgs['Body'].read()))
    df_day = df[df['created']==day]
    df_day['processed'] = df_day['text'].apply(lambda tweet: process_text(tweet))
    df_day['flagged'] = df_day['processed'].apply(lambda tweet: flagged_words(tweet))
    df_day = get_context_df(df_day)
    df_day['predicted'] = get_prediction(df_day)

    df_day = df_day.groupby(['flagged']).agg({'flagged': 'count', 'predicted': 'mean'})
    df_day.columns = ['frequency', 'predicted']
    df_day = df_day.reset_index().sort_values(by=["frequency","predicted"], ascending=False)
    df_day['date'] = day
    df_day['running_avg'] = df_day['flagged'].apply(lambda flagged: running_avg(priors,df_day,flagged))
    
    new_df = pd.concat([priors,df_day])
    csv_buffer = StringIO()
    new_df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    s3_resource.Bucket('trustar-dashboard-twitter').Object("running_avgs.csv").put(Body=csv_buffer.getvalue())
    print(f"{day} done!")
