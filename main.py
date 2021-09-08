import os
import sys
import html
import time
import os as _os
import dotenv as _dotenv

from constants import LOG
from twitter_bot import TwitterBot
from mention_analyzer import MentionAnalyzer
from last_seen import update_heroku_env_variable
from suggestion_retriever import SuggestionRetriever


def main():
    analyzer = MentionAnalyzer()
    suggester = SuggestionRetriever()
    bot = TwitterBot()
    
    while True:
        LOG.info(
            '----------------\n\t\t\t\t\t\t\t  ' \
            '----starting----\n\t\t\t\t\t\t\t  ' \
            '----------------'
        )

        bot.authorize()
        
        if len(sys.argv) > 1:
            # If we are testing the app
            if sys.argv[1] == 'test':
                LOG.info('Deleting all tweets')
                bot.delete_all_tweets()
                LOG.info('Tweeting test tweets')
                bot.tweet_test_tweets()
                exit()
            # If we just wanted to delete all tweets
            elif sys.argv[1] == 'clear':
                LOG.info('Deleting all tweets')
                bot.delete_all_tweets()
                LOG.info('exiting...')
                exit()
    
        # Retrieve all mentions tweeted after the last seen tweet id
        LOG.info('Polling mentions')
        mentions = bot.get_new_mentions()
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
            bot.reply_to_mention(help_message, media_info, mention._json['id'])

            # Delete the saved picture if necessary
            picture_file_path = media_info['picture_file_path']
            if picture_file_path:
                try:
                    os.remove(picture_file_path)
                    LOG.info(f'Deleted picture at {picture_file_path}')
                except Exception as err:
                    LOG.error(f'Failed to delete pictured at {picture_file_path}')
                    LOG.error(str(err))
            
            # Update last seen id
            update_heroku_env_variable('LAST_SEEN_ID', mention._json['id'])
            # Delay before next iteration
            time.sleep(1)

        LOG.info(' ')
        LOG.info('exiting...')
        
        # Wait 1 minute until next script execution
        time.sleep(60)


if __name__ == '__main__':
    main()
