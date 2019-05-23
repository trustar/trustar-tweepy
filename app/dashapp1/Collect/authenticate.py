import tweepy

def loadkeys(filename):
    '''
    input:  filename -- csv file with Twitter API authentification
    output: list with four strings
            - API key
            - API secret key
            - Access token
            - Access token secret
    '''
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items
    
def authenticate(twitter_auth_filename):
    '''
    Authenticate on Twitter
    '''
    keys = loadkeys(twitter_auth_filename)
    
    # auth = tweepy.OAuthHandler(keys[0],keys[1])
    # auth.set_access_token(keys[2], keys[3])
    auth = tweepy.AppAuthHandler(keys[0],keys[1]) # This allows to set API rates
    
    api = tweepy.API(auth, wait_on_rate_limit=True, 
                     wait_on_rate_limit_notify=True)
    return api