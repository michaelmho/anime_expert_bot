import tweepy
from red_tape import red_tape
# we can name this something else later just wanted to test this


def genre_finder(genre, mention):
    print(genre)
    api, FILENAME = red_tape()
    reply_tweet(api, mention)


def reply_tweet(api, mention):
    api.update_status('@' + mention.user.screen_name +
                      ' Hello World, I see you!', mention.id)
