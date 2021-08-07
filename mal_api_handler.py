import json
import time
import requests
import urllib.request

from random import randrange
from urllib.error import HTTPError
from PIL import Image, ImageEnhance
from constants import MEDIA_STATUSES, LOG

def mal_request_media(params):
    result = {
        'plot' : '',
        'title' : '',
        'image_file_path' : ''
    }

    base_url = f'https://api.jikan.moe/v3/search/{params["media_type"]}?page=1'

    # If this is a request with 'like'
    if params['query']:
        # Search for {media_type} with name like {query}
        encoded_query = urllib.parse.quote(params['query'])
        url = base_url + f'&q={encoded_query}'
    else:
        # Search for the top {limit} media with the requested genre(s)
        limit = 50
        genre = f'&genre={params["genre_ids"]}' if params['genre_ids'] else ''
        status = f'&status={MEDIA_STATUSES[params["media_type"]]}' if params['is_current'] else ''
        start_end = f'&start_date=1988-00-00&end_date=1998-00-00' if params['is_classic'] else ''
        url = base_url + f'{status}{genre}{start_end}&limit={limit}&order_by=score'

    # Make search request
    search_request = requests.get(url)
    search_request_response = search_request.json()

    LOG.info(f'Received status code {search_request.status_code} from {url}')

    # If the search request was NOT successful
    if search_request.status_code != 200:
        LOG.error(f'Response from api: {search_request_response}')
        return result
    
    # Array of all media returned
    returned_media = search_request_response['results']

    if len(returned_media) == 0:
        LOG.info(f'No media returned from {url}')
        return result

    # If this is a request with 'like', set index to zero in order to pull closeset match
    # Else set index to random index
    media_index = 0 if params['query'] else randrange(len(returned_media))
    selected_media = returned_media[media_index]

    # If this is a request with 'like'
    if params['query']:
        # Make a request for recommendations similar to the selected media
        url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/recommendations'
        recommendation_request = requests.get(url)
        recommendation_request_response = recommendation_request.json()

        LOG.info(f'Received status code {recommendation_request.status_code} from {url}')

        # If recommendation request is NOT successful
        if recommendation_request.status_code != 200:
            LOG.error(f'Response from api: {recommendation_request_response}')
            return result
        
        # Array of all recommendations returned
        returned_recommendations = recommendation_request_response['recommendations']

        if len(returned_recommendations) == 0:
            LOG.info(f'No recommendations returned from {url}')
            return result
        
        # Index of the returned recommendation we will select
        reccomendation_index = randrange(len(returned_recommendations))
        selected_media['mal_id'] = returned_recommendations[reccomendation_index]['mal_id']

        # Make a request for info on the selected recommendation
        url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}'
        media_info_request = requests.get(url)
        media_info_request_response = media_info_request.json()

        LOG.info(f'Received status code {media_info_request.status_code} from {url}')

        # If media info request is NOT successful
        if media_info_request.status_code != 200:
            LOG.error(f'Response from api: {media_info_request_response}')
            return result
        
        # Add the selected media's title and plot to the result
        try:
            result['title'] = media_info_request_response['title']
            result['plot'] = media_info_request_response['synopsis']
        except KeyError as err:
            LOG.error(f'The recommended media was missing one of the following keys ["title", "synopsis"]\recommended media: {media_info_request_response}')
            LOG.error(str(err))
            return result
    else:
        # Add the selected media's title and plot to the result
        try:
            result['title'] = selected_media['title']
            result['plot'] =  selected_media['synopsis']
        except KeyError as err:
            LOG.error(f'The selected media was missing one of the following keys ["title", "synopsis"]\nselected media: {selected_media}')
            LOG.error(str(err))
            return result

    # Request pictures urls for this media
    url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/pictures'
    picture_urls_request = requests.get(url)
    picture_urls_request_response = picture_urls_request.json()
    
    # If the request was NOT successful
    if picture_urls_request.status_code != 200:
        LOG.error(f'Received status code {picture_urls_request.status_code} from {url}\nResponse from api: {picture_urls_request_response}')
        return result
    
    LOG.info(f'Received status code {picture_urls_request.status_code} from {url}')
    picture_urls = picture_urls_request_response['pictures']

    if len(picture_urls) == 0:
        LOG.info(f'No picture urls returned from {url}')
        return result
    
    picture_index = randrange(len(picture_urls))
    
    # File path for media picture
    current_timestamp = int(time.time())
    image_file_path = f'./images/{selected_media["mal_id"]}_{current_timestamp}.png'

    try:
        # Open the picture file, and save the picture of the selected media
        image_file = open(image_file_path, 'w')
        urllib.request.urlretrieve(picture_urls[picture_index]['large'], image_file_path)
        image_file.close()
        
        # Open image file and then resize and enhance using PIL 
        image_file = Image.open(image_file_path)
        enhancer = ImageEnhance.Sharpness(image_file)   
        enhancer = enhancer.enhance(2)
        enhancer.save(image_file_path, quality=95)

        # Add image file path to result
        result['image_file_path'] = image_file_path
    except IOError as err:
        LOG.error(f'Problem opening file {image_file_path}')
        LOG.error(str(err))
    except HTTPError as err:
        LOG.error(f'Received status code {err.code} from "{selected_media["image_url"]}"')

    return result
