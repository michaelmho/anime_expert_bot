import json
import tweepy
import os as _os

from constants import LOG, API_KEY, API_SECRET, ACCESS_KEY, ACCESS_SECRET

class TwitterBot():
    def __init__(self):
        pass
    

    def authorize(self):
        try:  
            auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            self.api = tweepy.API(auth)
        except Exception as err:
            LOG.error(f'Could not connect to the twitter api')
            LOG.error(f'{str(err)}')
            LOG.info('exiting...')
            exit()

    
    def get_new_mentions(self):
        return self.api.mentions_timeline(int(_os.environ['LAST_SEEN_ID']))


    def write_tweet(self, help_message, title, plot):
        if title and plot:
            if help_message:
                reply_text =f'There\'s a problem with your request: {help_message}. ' \
                            f'But maybe you\'ll like this\n' \
                            f'Title: {title}\n' \
                            f'Plot: {plot}'
            else:
                reply_text = f'Title: {title}\nPlot: {plot}'        
        else:
            reply_text = 'Sorry, I encountered a problem while getting your suggestion'
        
        if len(reply_text) >= 276:
            return reply_text[0:272] + '...'
        
        return reply_text


    def reply_to_mention(self, help_message, media_info, mention_id):
        reply_text = self.write_tweet(help_message, media_info['title'], media_info['plot'])
        LOG.info(f'Replying to tweet with "{reply_text}"')

        picture_file_path = media_info['picture_file_path']
        try:
            if picture_file_path:
                self.api.update_with_media(picture_file_path, reply_text, in_reply_to_status_id = mention_id)
            else:
                self.api.update_status(reply_text, in_reply_to_status_id = mention_id)
        except Exception as err:
            LOG.error('Failed to reply')
            LOG.error(str(err))


    def delete_all_tweets(self):
        LOG.info('Deleting all tweets')
        for status in tweepy.Cursor(self.api.user_timeline).items():
            try:
                self.api.destroy_status(status.id)
                LOG.info(f'Deleted: {status.id}')
            except Exception as err:
                LOG.error(f'Failed to delete: {status.id}')
                LOG.error(str(err))


    def tweet_test_tweets(self):
        LOG.info('Tweeting test tweets')
        tweets = [
            '@AnimeExpertBot police',
            '@AnimeExpertBot anime manga',
            '@AnimeExpertBot current manga',
            '@AnimeExpertBot action action',
            '@AnimeExpertBot classic action',
            '@AnimeExpertBot current classic',
            '@AnimeExpertBot classic current',
            '@AnimeExpertBot adventure action',
            '@AnimeExpertBot manga like mierko',
            '@AnimeExpertBot manga current sci-fi',
            '@AnimeExpertBot like attack on titan',
        ]

        for tweet in tweets:
            try:
                self.api.update_status(tweet)
                LOG.info(f'Tweeted: {tweet}')
            except Exception as err:
                LOG.error(f'Failed to tweet: {tweet}')
                LOG.error(str(err))
 