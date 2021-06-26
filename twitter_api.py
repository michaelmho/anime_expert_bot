import tweepy

def get_reply_text(media_info):
    tweet_text = ''
    media_info_keys = media_info.keys()

    if len(media_info['title']) > 0:
        if len(media_info['synopsis']) > 0:
            if len(media_info['image_file_path']) > 0:
                tweet_text = f'Title: {media_info["title"]}\nSynopsis: {media_info["synopsis"]}'
                
                if len(tweet_text) >= 280:
                    tweet_text = tweet_text[0:275] + '...'
    
    return tweet_text

def reply_to_tweet(api, image_file_path, tweet_text, mention_id):
    api.update_with_media(image_file_path, tweet_text, in_reply_to_status_id = mention_id)