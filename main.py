import json
import tweepy
from genre_finder import genre_finder
from last_seen import get_last_seen_id, set_last_seen_id


def main():
    # open and read file
    cred_file = open("credentials.json", "r")
    cred = cred_file.read()
    FILENAME = "last_seen.txt"

    # parse
    credentials = json.loads(cred)

    # Getting credentials from credentials.json

    auth = tweepy.OAuthHandler(
        credentials["API_KEY"], credentials["API_SECRET"])
    auth.set_access_token(
        credentials["ACCESS_KEY"], credentials["ACCESS_SECRET"])
    api = tweepy.API(auth)

    # prints mentions as an array

    last_seen_id = get_last_seen_id(FILENAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')

    for mention in reversed(mentions):
        tweet_text = mention.full_text.lower()
        last_seen_id = mention.id
        set_last_seen_id(last_seen_id, FILENAME)

        if(len(tweet_text) > 13):
            # TODO: fix this, all this does is check if there is more text after the mention
            switch_genre("Action", tweet_text)


def switch_genre(genre, tweet_text):
    switcher = {
        genre: genre_finder(tweet_text),
    }

    return switcher.get(genre, "empty")


if __name__ == '__main__':
    main()
