import os
import sys
import html
import time
import os as _os
import dotenv as _dotenv

from constants import LOG
from mal_api_handler import get_media_suggestion
from mention_handler import parse_mention, get_reply_text
from twitter_api_handler import get_twitter_api, reply_to_tweet, delete_all_tweets, tweet_test_tweets


_dotenv.load_dotenv()

def main():
    while True:
        LOG.info('----------------')
        LOG.info('----------------')
        LOG.info('----------------')    

        twitter_api, last_seen_file_name = get_twitter_api()
        
        # # If we are testing the app
        # if sys.argv[1] == 'test':
        #     LOG.info('Deleting all tweets')
        #     delete_all_tweets(twitter_api)
        #     LOG.info('Tweeting test tweets')
        #     tweet_test_tweets(twitter_api)
        # # If we just wanted to delete all tweets
        # elif sys.argv[1] == 'clear':
        #     LOG.info('Deleting all tweets')
        #     delete_all_tweets(twitter_api)
        #     LOG.info('exiting...')
        #     exit()
    
        # Get all mentions tweeted after the last seen tweet id
        LOG.info('Polling mentions')
        mentions = twitter_api.mentions_timeline(int(_os.environ['LAST_SEEN_ID']))
        LOG.info(f'Found {len(mentions)} new mentions')
        
        # Respond to mentions from newest to oldest
        for mention in reversed(mentions):
            LOG.info(' ')
            mention_text = html.unescape(mention._json['text'])
            LOG.info(f'Parsing mention: {mention_text}')

            # Parse the mention
            help_message, mal_request_params = parse_mention(mention_text)
            LOG.info(f'Returned {help_message}, {mal_request_params}')

            # Make a mal api request based on the mention
            media_info = get_media_suggestion(mal_request_params)
            LOG.info(f'Returned {media_info}')

            # Respond to the mention
            reply_text = get_reply_text(help_message, media_info)
            LOG.info(f'Replying to tweet with "{reply_text}"')
            reply_to_tweet(twitter_api, media_info['picture_file_path'], reply_text, mention._json['id'])

            # Delete media image
            if media_info['picture_file_path']:
                os.remove(media_info['picture_file_path'])

        # Set the last seen tweet id to the id if the last parsed mention
        _os.environ['LAST_SEEN_ID'] = str(mentions[-1]._json['id'])

        LOG.info(' ')
        LOG.info('exiting...')

        # Wait 1 minute until next script execution
        time.sleep(60)


if __name__ == '__main__':
    main()
