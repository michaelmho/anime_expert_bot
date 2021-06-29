import tweepy
import os
import logging
import logging.handlers as handlers
from last_seen import get_last_seen_id, set_last_seen_id
from mention_handler import parse_mention
from twitter_api_handler import get_twitter_api, get_reply_text, reply_to_tweet
from mal_api_handler import mal_api_request

rfh = logging.handlers.RotatingFileHandler(
    filename='./text_files/aeb.log',
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=2,
    encoding=None,
    delay=0
)

logging.basicConfig(
    format='[%(levelname)s] %(asctime)s : %(message)s', 
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        rfh
    ]
)


def main():
    log = logging.getLogger()

    twitter_api, last_seen_file_name = get_twitter_api()

    # Get all mentions tweeted after the last seen tweet id
    last_seen_id = get_last_seen_id(last_seen_file_name)
    log.info('----------------')
    log.info('Polling mentions')
    mentions = twitter_api.mentions_timeline(last_seen_id)
    log.info(f'Found {len(mentions)} new mentions')
    
    # Respond to mentions from newest to oldesr
    for mention in reversed(mentions):
        mention_text = mention._json['text']
        log.info(f'Parsing mention: {mention_text}')

        # Parse the mention
        message, mal_api_request_params = parse_mention(mention_text)
        log.info(f'Returned {message}, {mal_api_request_params}')

        # Make a mal api request based on the mention
        media_info = mal_api_request(mal_api_request_params)

        # Respond to the mention
        reply_text = get_reply_text(message, media_info)
        log.info(f'Replying to tweet with "{reply_text}"')
        reply_to_tweet(twitter_api, media_info['image_file_path'], reply_text, mention._json['id'])
        
        # Delete anime cover photo
        os.remove(media_info['image_file_path'])
        
        log.info(' ')

    # Set the last seen tweet id to the id if the last parsed mention
    last_seen_id = mentions[-1]._json['id']
    set_last_seen_id(last_seen_id, last_seen_file_name)


if __name__ == '__main__':
    main()
