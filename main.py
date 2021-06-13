import tweepy
import os

API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET_KEY")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
ACCESS_KEY = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")


auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(API_KEY, API_SECRET)
api = tweepy.API(auth)

print(BEARER_TOKEN)
