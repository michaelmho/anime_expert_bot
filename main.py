import os
import sys
import html
import time
import logging
import logging.handlers as handlers

from mal_api_handler import mal_request_media
from last_seen import get_last_seen_id, set_last_seen_id
from mention_handler import parse_mention, get_reply_text
from twitter_api_handler import get_twitter_api, reply_to_tweet, delete_all_tweets, post_test_tweets

rfh = logging.handlers.RotatingFileHandler(
    filename='./text_files/aeb.log',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding='utf-8',
    mode='a',
    delay=0
)

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s : %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        rfh
    ]
)


def main():
    log = logging.getLogger()
    log.info('----------------')
    log.info('----------------')
    log.info('----------------')    

    twitter_api, last_seen_file_name = get_twitter_api()

    # If we are testing the app
    if sys.argv[1] == 'test':
        delete_all_tweets(twitter_api)
        post_test_tweets(twitter_api)
    # If we just wanted to delete all tweets
    elif sys.argv[1] == 'clear':
        delete_all_tweets(twitter_api)
        exit()
    
    # Get all mentions tweeted after the last seen tweet id
    last_seen_id = get_last_seen_id(last_seen_file_name)
    log.info('Polling mentions')
    mentions = twitter_api.mentions_timeline(last_seen_id)
    log.info(f'Found {len(mentions)} new mentions')
    
    # Respond to mentions from newest to oldest
    for mention in reversed(mentions):
        log.info(' ')
        mention_text = html.unescape(mention._json['text'])
        log.info(f'Parsing mention: {mention_text}')

        # Parse the mention
        help_message, mal_request_params = parse_mention(mention_text)
        log.info(f'Returned {help_message}, {mal_request_params}')

        # Make a mal api request based on the mention
        media_info = mal_request_media(mal_request_params)
        log.info(f'Returned {media_info}')

        # Respond to the mention
        reply_text = get_reply_text(help_message, media_info)
        log.info(f'Replying to tweet with "{reply_text}"')
        reply_to_tweet(twitter_api, media_info['image_file_path'], reply_text, mention._json['id'])

        # Delete media image
        if media_info['image_file_path']:
            os.remove(media_info['image_file_path'])
        
        # Delay to keep from reaching mal api request limits
        time.sleep(1)

    # Set the last seen tweet id to the id if the last parsed mention
    last_seen_id = mentions[-1]._json['id']
    set_last_seen_id(last_seen_id, last_seen_file_name)


if __name__ == '__main__':
    main()
