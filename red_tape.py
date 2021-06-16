import json
import tweepy


def red_tape():
    # open and read file
    cred_file = open("./text_files/credentials.json", "r")
    cred = cred_file.read()
    FILENAME = "./text_files/last_seen.txt"

    # parse
    credentials = json.loads(cred)

    # Getting credentials from credentials.json

    auth = tweepy.OAuthHandler(
        credentials["API_KEY"], credentials["API_SECRET"])
    auth.set_access_token(
        credentials["ACCESS_KEY"], credentials["ACCESS_SECRET"])
    api = tweepy.API(auth)

    return(api, FILENAME)
