import json
import tweepy


def get_twitter_api():
    # open and read credentials file
    cred_file = open("./text_files/credentials.json", "r")
    cred = cred_file.read()

    # parse
    credentials = json.loads(cred)

    # Getting credentials from credentials.json

    auth = tweepy.OAuthHandler(
        credentials["API_KEY"], credentials["API_SECRET"])
    auth.set_access_token(
        credentials["ACCESS_KEY"], credentials["ACCESS_SECRET"])
    api = tweepy.API(auth)

    return api, "./text_files/last_seen.txt"    

def get_reply_text(message, media_info):
    if message == '':
        message_text = ''
    else:
        message_text = f'There\'s a problem with your request: {message}\nBut maybe you\'ll like this\n'

    media_info_text = 'Sorry, I encountered a problem while getting your suggestion'
    if len(media_info['title']) > 0:
        if len(media_info['plot']) > 0:
            if len(media_info['image_file_path']) > 0:
                media_info_text = f'Title: {media_info["title"]}\nPlot: {media_info["plot"]}'
    
    reply_text = message_text + media_info_text
    if len(reply_text) > 280:
        reply_text = reply_text[0:277] + '...'
    
    return reply_text

def reply_to_tweet(api, image_file_path, reply_text, mention_id):
    api.update_with_media(image_file_path, reply_text, in_reply_to_status_id = mention_id)