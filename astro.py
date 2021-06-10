import tweepy

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_KEY = ""
ACCESS_SECRET = ""

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET);
auth.set_access_token(CONSUMER_KEY, CONSUMER_SECRET)
api = tweepy.API(auth)

print("hellow world")