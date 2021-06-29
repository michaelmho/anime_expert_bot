import json
import tweepy


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
    api.update_with_media(image_file_path, reply_text, in_reply_to_status_id = mention_id)