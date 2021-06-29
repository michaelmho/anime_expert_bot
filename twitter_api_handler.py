import json
import tweepy
import logging

log = logging.getLogger(__name__)

def get_twitter_api():
    # open and read credentials file
    cred_file = open("./text_files/credentials.json", "r")
    cred = cred_file.read()

    # parse
    credentials = json.loads(cred)

    # Getting credentials from credentials.json

    auth = tweepy.OAuthHandler(
        credentials["API_KEY"], credentials["API_SECRET"])
    auth.set_access_token(
        credentials["ACCESS_KEY"], credentials["ACCESS_SECRET"])
    api = tweepy.API(auth)

    return api, "./text_files/last_seen.txt"    


def reply_to_tweet(api, image_file_path, reply_text, mention_id):
    try:
        if image_file_path == '':
            api.update_status(reply_text, in_reply_to_status_id = mention_id)
        else:
            api.update_with_media(image_file_path, reply_text, in_reply_to_status_id = mention_id)
    except Exception as err:
        log.error("Failed to reply")
        log.error(err)


def delete_all_tweets(api):
    for status in tweepy.Cursor(api.user_timeline).items():
        try:
            api.destroy_status(status.id)
            print("Deleted:", status.id)
        except Exception:
            print("Failed to delete:", status.id)

def post_test_tweets(api):
    tweets = [
        '@AnimeExpertBot current manga',
        '@AnimeExpertBot adventure action',
        '@AnimeExpertBot action action',
        '@AnimeExpertBot anime manga',
        '@AnimeExpertBot asdhbasdasd',
        '@AnimeExpertBot 123124^&asdasd',
        '@AnimeExpertBot vu le 14224',
        '@AnimeExpertBot police',
        '@AnimeExpertBot comedy hentai demons'
    ]

    for tweet in tweets:
        api.update_status(tweet)

    