import os
import sys
import json
import jsonpickle

import tweepy
from datetime import datetime

from authenticate import *
from read_outputs import *

# Refactor from https://bhaskarvk.github.io/2015/01/how-to-use-twitters-search-rest-api-most-effectively./
# This function collects tweets from most recent ones to the oldest ones. 
def collect_tweets(query):

	# Authenticate
	twitter_auth_filename = "twitter.csv"
	api = authenticate(twitter_auth_filename)


	# Create new directory
	if os.path.isdir("output") is False:
		os.mkdir("output")
	directory = "output"


	# Write a new file
	today = datetime.today()
	today = str(today.year) + "-" + str(today.month) + "-" + str(today.day) + "_at_" + str(today.hour) + "h" + str(today.minute) + "m" + str(today.second) + "s"
	file = '{}/output-{}-{}.txt'.format(directory,today,query[0:10])


	tweets_per_qry = 100 #100 is max number allowed by Twitter
	stop = 1000000 # Stop when you collect this number of tweets.
	min_id = None # create interval. None means go as far back as Twitter allows.
	max_id = -1 # create interval. -1 means start from the most recent one.
	tweet_count = 0

	# Main Corpus
	print('########################', flush=True)
	print(f'Time: {today}', flush=True)
	f = open(file,'w')
	while tweet_count<stop: 
		# Fetch
		if (max_id <= 0):
			if (not min_id):
				new_tweets = api.search(q=query, count=tweets_per_qry,
										tweet_mode='extended')
			else:
				new_tweets = api.search(q=query, count=tweets_per_qry,
										since_id=min_id,
										tweet_mode='extended')
		else:
			if (not min_id):
				new_tweets = api.search(q=query, count=tweets_per_qry,
										max_id=str(max_id - 1),
										tweet_mode='extended')
			else:
				new_tweets = api.search(q=query, count=tweets_per_qry,
										max_id=str(max_id - 1),
										since_id=min_id,
										tweet_mode='extended')
									
		# If query returns empty
		if not new_tweets:
			print("No more tweets found", flush=True)
			break

		# Save to file
		for tweet in new_tweets:
			f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
		f.flush()
		
		# Flag    
		tweet_count += len(new_tweets)
		print(f"Downloaded {tweet_count} tweets", flush=True)
		
		# Search tweets older than the last one collected.
		max_id = new_tweets[-1].id
	
	f.close()
	df = pd.read_csv("tweets.csv")
	pd.concat([df,tweets_df(file, path=False)]).drop_duplicates(subset=['id']).to_csv("tweets.csv", index=False)
		
	# Success        
	print(f'Query: {query}', flush=True)
	print(f"Downloaded {tweet_count} tweets, saved to {file}", flush=True)
	print('--------------------------------------------------------------', flush=True)