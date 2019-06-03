import os
import json
import pandas as pd
import dateutil.parser


def tweets_list(file):
    '''
    Read a json file and extract relevant tweet information
    '''
    lines = open(file, "r")
    tweets_list = []
    for line in lines:
        tweet = json.loads(line)
        tweet_dictionary = {}
        tweet_dictionary['id'] = tweet["id"]
        tweet_dictionary['text'] = tweet["full_text"]
        tweet_dictionary['created'] = dateutil.parser.parse(tweet["created_at"])
        tweet_dictionary['language'] = tweet["lang"]
        tweets_list.append(tweet_dictionary)
    lines.close()
    return tweets_list
    

def tweets_df(directory, path=True):
    '''
    input: directoy with output files. Example "Output/". Select false if passing a single .txt file.
    output: Data frame with unique tweets
    '''
    if path:
        outputs = list(map(lambda output: directory+"/"+output,filter(lambda output: output[-4:]==".txt",os.listdir(directory))))
    else:
        outputs = [directory]
    tweets = []
    for output in outputs:
        temp = tweets_list(output)
        tweets += temp
    tweets = pd.DataFrame(tweets)
    tweets = tweets[tweets['language']=="en"]
    tweets = tweets.drop(['language'], axis=1)
    tweets = tweets.drop_duplicates(subset=['id'])
    tweets = tweets.reset_index().drop(['index'],axis=1)
    return tweets
