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
    bot = TwitterBot()
    analyzer = MentionAnalyzer()
    suggester = SuggestionRetriever()
    
    while True:
        LOG.info('----------------')
        LOG.info('----starting----')
        LOG.info('----------------')

        # Authorize bots connection to twitter
        bot.authorize()
        
        # Check for custom command line arguments
        if len(sys.argv) > 1:
            # If we are testing the app
            if sys.argv[1] == 'test':
                bot.delete_all_tweets()
                bot.tweet_test_tweets()
                LOG.info('exiting...')
                exit()
            # If we just wanted to delete all tweets
            elif sys.argv[1] == 'clear':
                bot.delete_all_tweets()
                LOG.info('exiting...')
                exit()
    
        # Check for new mentions
        mentions = bot.get_new_mentions()
        mentionQunatity = len(mentions)
        LOG.info(f'Found {mentionQunatity} new mentions\n')

        # Respond to each new mention
        for i in reversed(range(mentionQunatity)):
            LOG.info(f'{mentionQunatity - i}/{mentionQunatity}')

            mention_text = html.unescape(mentions[i]._json['text'])
            mention_id = mentions[i]._json['id']

            # Analyze the mention
            help_message, search_criteria = analyzer.analyze(mention_text)

            # Retrieve a suggestion from the mal api based on the search criteria
            media_info = suggester.get_suggestion(search_criteria)

            # Respond to the mention
            bot.reply_to_mention(help_message, media_info, mention_id)

            # Delete the saved picture if necessary
            picture_file_path = media_info['picture_file_path']
            if picture_file_path:
                try:
                    os.remove(picture_file_path)
                    LOG.info(f'> Deleted picture at {picture_file_path}\n')
                except Exception as err:
                    LOG.error(f'> Failed to delete pictured at {picture_file_path}\n')
                    LOG.error(str(err))
            
            # Update last seen id
            update_heroku_env_variable('LAST_SEEN_ID', mention_id)

        LOG.info('exiting...')
        time.sleep(60)


if __name__ == '__main__':
    main()
