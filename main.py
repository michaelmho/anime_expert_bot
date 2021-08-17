import os
import sys
import html
import time
import os as _os
import dotenv as _dotenv

from constants import LOG
from mention_analyzer import MentionAnalyzer
from last_seen import update_heroku_env_variable
from suggestion_retriever import SuggestionRetriever
from twitter_api import get_twitter_api, reply_to_tweet, delete_all_tweets, tweet_test_tweets

_dotenv.load_dotenv()
TOKEN = _os.environ['TOKEN']

def main():
    analyzer = MentionAnalyzer()
    suggester = SuggestionRetriever()
    
    while True:
        LOG.info('----------------\n----------------\n----------------') 

        twitter_api = get_twitter_api()
        
        if len(sys.argv) > 1:
            # If we are testing the app
            if sys.argv[1] == 'test':
                LOG.info('Deleting all tweets')
                delete_all_tweets(twitter_api)
                LOG.info('Tweeting test tweets')
                tweet_test_tweets(twitter_api)
            # If we just wanted to delete all tweets
            elif sys.argv[1] == 'clear':
                LOG.info('Deleting all tweets')
                delete_all_tweets(twitter_api)
                LOG.info('exiting...')
                exit()
    
        # Retrieve all mentions tweeted after the last seen tweet id
        LOG.info('Polling mentions')
        mentions = twitter_api.mentions_timeline(int(_os.environ['LAST_SEEN_ID']))
        LOG.info(f'Found {len(mentions)} new mentions')
        
        # Respond to mentions from newest to oldest
        for mention in reversed(mentions):
            LOG.info(' ')
            mention_text = html.unescape(mention._json['text'])
            LOG.info(f'Parsing mention: {mention_text}')

            # Analyze the mention
            help_message, mal_search_criteria = analyzer.analyze(mention_text)
            LOG.info(f'Returned help_message:{help_message}, mal_search_criteria:{mal_search_criteria}')

            # Retrieve a suggestion from the mal api based on the search criteria
            media_info = suggester.get_suggestion(mal_search_criteria)
            LOG.info(f'Returned media_info:{media_info}')

            # Respond to the mention
            reply_to_tweet(twitter_api, help_message, media_info, mention._json['id'])

            # Delete the saved picture if necessary
            picture_file_path = media_info['picture_file_path']
            if picture_file_path:
                try:
                    os.remove(picture_file_path)
                    LOG.info(f'Deleted picture at {picture_file_path}')
                except Exception as err:
                    LOG.error(f'Failed to delete pictured at {picture_file_path}')
                    LOG.error(str(err))

        if len(mentions) > 0:
            update_heroku_env_variable(TOKEN, 'LAST_SEEN_ID', mentions[-1]._json['id'])

        LOG.info(' ')
        LOG.info('exiting...')

        # Wait 1 minute until next script execution
        time.sleep(60)


if __name__ == '__main__':
    main()
