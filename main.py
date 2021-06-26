import tweepy
import os
import logging
import logging.handlers as handlers
from red_tape import red_tape
from last_seen import get_last_seen_id, set_last_seen_id
from commands import parse_mention
from twitter_api import get_reply_text, reply_to_tweet

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

    api, FILENAME = red_tape()

    last_seen_id = get_last_seen_id(FILENAME)
    log.info('----------------')
    log.info('Polling mentions')
    mentions = api.mentions_timeline(last_seen_id)
    log.info(f'Found {len(mentions)} new mentions')
    
    for mention in reversed(mentions):
        mention_text = mention._json['text']
        log.info(f'Parsing mention: {mention_text}')

        media_info = parse_mention(mention_text)
        log.info(f'media_info: {media_info}')

        reply_text = get_reply_text(media_info)
        if len(reply_text) > 0:
            log.info(f'Replying to tweet with "{reply_text}"')
            reply_to_tweet(api, media_info['image_file_path'], reply_text, mention._json['id'])
            os.remove(media_info['image_file_path'])
        
        log.info(' ')

    last_seen_id = mentions[-1]._json['id']
    set_last_seen_id(last_seen_id, FILENAME)


if __name__ == '__main__':
    main()
