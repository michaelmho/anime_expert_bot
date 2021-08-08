import json
import time
import requests
import urllib.request

from random import randrange
from urllib.error import HTTPError
from PIL import Image, ImageEnhance
from constants import MEDIA_STATUSES, LOG


def get_media_suggestion(params):
    result = {
        'plot' : '',
        'title' : '',
        'picture_file_path' : ''
    }

    base_url = f'https://api.jikan.moe/v3/search/{params["media_type"]}?page=1'

    # If this is a mention with 'like'
    if params['query']:
        # Form url to search for {media_type} with name like {query}
        encoded_query = urllib.parse.quote(params['query'])
        url = base_url + f'&q={encoded_query}'
    else:
        # Form url to search for the top {limit} media with the requested genre(s)
        limit = 50
        genre = f'&genre={params["genre_ids"]}' if params['genre_ids'] else ''
        status = f'&status={MEDIA_STATUSES[params["media_type"]]}' if params['is_current'] else ''
        start_end = f'&start_date=1988-00-00&end_date=1998-00-00' if params['is_classic'] else ''
        url = base_url + f'{status}{genre}{start_end}&limit={limit}&order_by=score'

    # Make the search request
    returned_media = handle_api_request(url, 'results')
    # If the was any problem with the request, return
    if not returned_media:
        return result

    # Select 1 of the returned media
    # If this is a mention with 'like', set index to zero in order to pull closeset match
    # Else set the index at random
    media_index = 0 if params['query'] else randrange(len(returned_media))
    selected_media = returned_media[media_index]

    # If this is a mention with 'like'
    if params['query']:
        # Make a request for recommendations similar to the selected media
        url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/recommendations'
        returned_recommendations = handle_api_request(url, 'recommendations')
        # If the was any problem with the request, return
        if not returned_recommendations:
            return result
        
        # Select a random recommendation
        reccomendation_index = randrange(len(returned_recommendations))
        selected_media['mal_id'] = returned_recommendations[reccomendation_index]['mal_id']

        # Make a request for details on the selected media        
        url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}'
        returned_media_details = handle_api_request(url, '')
        # If the was any problem with the request, return
        if not returned_media_details:
            return result
        
        # Add the selected media's details to the result
        try:
            result['title'] = returned_media_details['title']
            result['plot'] = returned_media_details['synopsis']
        except KeyError as err:
            LOG.error(f'The recommended media was missing one of the following keys ["title", "synopsis"]\nRecommended media: {returned_media_details}')
            LOG.error(str(err))
            return result
    else:
        # Add the selected media's title and plot to the result
        try:
            result['title'] = selected_media['title']
            result['plot'] =  selected_media['synopsis']
        except KeyError as err:
            LOG.error(f'The selected media was missing one of the following keys ["title", "synopsis"]\nSelected media: {selected_media}')
            LOG.error(str(err))
            return result

    # Request picture urls for the selected media
    url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/pictures'
    returned_picture_urls = handle_api_request(url, 'pictures')
    # If the was any problem with the request, return
    if not returned_picture_urls:
        return result
    
    # Select a random picture url
    picture_index = randrange(len(returned_picture_urls))
    selected_picture_url = returned_picture_urls[picture_index]['large']
    
    # Set the file path for the picture of the selected media
    current_timestamp = int(time.time())
    picture_file_path = f'./images/{selected_media["mal_id"]}_{current_timestamp}.png'

    try:
        # Create a picture file
        image_file = open(picture_file_path, 'w')
        # Request the picture of the selected media from the selected picture url
        # Save it to the picture file path
        urllib.request.urlretrieve(selected_picture_url, picture_file_path)
        image_file.close()
        
        # Open picture file and enhance the quality using PIL 
        image_file = Image.open(picture_file_path)
        enhancer = ImageEnhance.Sharpness(image_file)   
        enhancer = enhancer.enhance(2)
        enhancer.save(picture_file_path, quality=95)

        # Add picture file path to result
        result['picture_file_path'] = picture_file_path
    except IOError as err:
        LOG.error(f'Problem opening file {picture_file_path}')
        LOG.error(str(err))
    except HTTPError as err:
        LOG.error(f'Received status code {err.code} from "{selected_media["image_url"]}"')

    return result


def handle_api_request(url, json_key):
    try:
        response = requests.get(url, timeout=(5,12))
    except requests.exceptions.Timeout as err:
        LOG.error(f'Timeout on {url}: {str(err)}')
        return []

    if response.status_code != 200:
        LOG.error(f'Received status code {response.status_code} from {url}\nApi response: {response.json()}')
        return []

    LOG.info(f'Received status code {response.status_code} from {url}')

    if json_key:
        try:
            results = (response.json())[json_key]
        except KeyError as err:
            LOG.error(f'Response missing key \"{json_key}\"')
            LOG.error(str(err))
            return []        

        if len(results) == 0:
            LOG.info(f'No results returned from {url}')
    else:
        results = response.json()

    return results 
