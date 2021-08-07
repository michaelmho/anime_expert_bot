import json
import tweepy
from constants import LOG


def get_twitter_api():
    # Open and read credentials file
    try:
        cred_file = open('./text_files/credentials.json', 'r')
        cred = cred_file.read()
    except Exception as err:
        LOG.error(f'Could not access credentials.json: {str(err)}')
        LOG.info('exiting...')
        exit()

    # Parse credentials file
    credentials = json.loads(cred)

    # Authorize connection to the twitter api
    auth = tweepy.OAuthHandler(credentials['API_KEY'], credentials['API_SECRET'])
    auth.set_access_token(credentials['ACCESS_KEY'], credentials['ACCESS_SECRET'])
    api = tweepy.API(auth)

    return api, './text_files/last_seen.txt'    


def reply_to_tweet(api, picture_file_path, reply_text, mention_id):
    try:
        if picture_file_path == '':
            api.update_status(reply_text, in_reply_to_status_id = mention_id)
        else:
            api.update_with_media(picture_file_path, reply_text, in_reply_to_status_id = mention_id)
    except Exception as err:
        LOG.error('Failed to reply')
        LOG.error(str(err))


def delete_all_tweets(api):
    for status in tweepy.Cursor(api.user_timeline).items():
        try:
            api.destroy_status(status.id)
            LOG.info(f'Deleted: {status.id}')
        except Exception:
            LOG.error(f'Failed to delete: {status.id}')


def post_test_tweets(api):
    tweets = [
        '@AnimeExpertBot current classic',
        '@AnimeExpertBot classic current',
        '@AnimeExpertBot current manga',
        '@AnimeExpertBot adventure action',
        '@AnimeExpertBot action action',
        '@AnimeExpertBot anime manga',
        '@AnimeExpertBot police',
        '@AnimeExpertBot like attack on titan',
        '@AnimeExpertBot classic action',
        '@AnimeExpertBot manga like mierko',
        '@AnimeExpertBot we are like the champions',
        '@AnimeExpertBot manga current sci-fi like',
    ]

    for tweet in tweets:
        try:
            api.update_status(tweet)
            LOG.info(f'Tweeted: {tweet}')
        except Exception:
            LOG.error(f'Failed to tweet: {tweet}')

    