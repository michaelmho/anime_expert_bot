import tweepy
from red_tape import red_tape
from genre_finder import genre_finder
from last_seen import get_last_seen_id, set_last_seen_id


def main():
    api, FILENAME = red_tape()

    # prints mentions as an array

    last_seen_id = get_last_seen_id(FILENAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')

    for mention in reversed(mentions):
        tweet_text = mention.full_text.lower()
        last_seen_id = mention.id
        set_last_seen_id(last_seen_id, FILENAME)

        if(len(tweet_text) > 13):
            # TODO:: fix this, all this does is check if there is more text after the mention and sends the whole tweet
            switch_genre(tweet_text, mention)


def switch_genre(genre, mention):
    # this will most likely go in another file, but it is convenient to leave here for now
    switcher = {
        genre: genre_finder(genre, mention),
    }

    return switcher.get(genre, "empty")


if __name__ == '__main__':
    main()
