import os
import time
from collect_tweets import *

# Check if there are queries
queries = []
if os.path.isdir("queries") is False:
    print('ALERT: No queries folder found.', flush=True)
else: 
    queries = [f for f in os.listdir("queries") if f.endswith('.txt')]
    

print(f'---***!!! START OF NEW COLLECTION !!!***---', flush=True)
flag = 0    
for q in queries:
    malware_words = []
    q_file = open("queries/"+q, "r")
    for line in q_file.readlines():
        malware_words.append(line.strip())
    q_file.close()
    mw = " OR ".join(malware_words)
    mw += " -filter:retweets"
    query = mw
    collect_tweets(query)
    flag += 1
    
    
if flag == len(queries):
	print(f'SUCCESS', flush=True)
else:
	print(f'CAREFUL', flush=True)  
	 
print(f'---***!!! END OF NEW COLLECTION !!!***---', flush=True)    