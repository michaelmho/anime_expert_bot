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
        'picture_file_path' : ''
    }

    base_url = f'https://api.jikan.moe/v3/search/{params["media_type"]}?page=1'

    # If this is a mention with 'like'
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
    try:
        search_response = requests.get(url, timeout=(3,5))
    except requests.exceptions.Timeout as err:
        LOG.error(f'Timeout on {url}: {str(err)}')
        return result
    
    search_response_json = search_response.json()

    # If the search request was NOT successful
    if search_response.status_code != 200:
        LOG.error(f'Received status code {search_response.status_code} from {url}\nResponse from api: {search_response_json}')
        return result

    LOG.info(f'Received status code {search_response.status_code} from {url}')        
    
    # Array of all media returned from the seach request
    returned_media = search_response_json['results']

    # If no media was returned from the search request
    if len(returned_media) == 0:
        LOG.info(f'No media returned from {url}')
        return result

    # If this is a mention with 'like', set index to zero in order to pull closeset match
    # Else set index to random index
    media_index = 0 if params['query'] else randrange(len(returned_media))
    selected_media = returned_media[media_index]

    # If this is a mention with 'like'
    if params['query']:
        # Make a request for recommendations similar to the selected media
        try:
            url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/recommendations'
            recommendations_response = requests.get(url, timeout=(3,5))
        except requests.exceptions.Timeout as err:
            LOG.error(f'Timeout on {url}: {str(err)}')
            return result
        
        recommendations_response_json = recommendations_response.json()

        # If recommendations request is NOT successful
        if recommendations_response.status_code != 200:
            LOG.error(f'Received status code {recommendations_response.status_code} from {url}\nResponse from api: {recommendations_response_json}')
            return result

        LOG.info(f'Received status code {recommendations_response.status_code} from {url}')
        
        # Array of all recommendations returned
        returned_recommendations = recommendations_response_json['recommendations']

        # If no recommendations returned
        if len(returned_recommendations) == 0:
            LOG.info(f'No recommendations returned from {url}')
            return result
        
        # Select the mal_id of a random recommendation
        reccomendation_index = randrange(len(returned_recommendations))
        selected_media['mal_id'] = returned_recommendations[reccomendation_index]['mal_id']

        # Make a request for details on the selected recommendation        
        try:
            url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}'
            media_details_response = requests.get(url, timeout=(3,5))
        except requests.exceptions.Timeout as err:
            LOG.error(f'Timeout on {url}: {str(err)}')
            return result
        
        media_details_response_json = media_details_response.json()

        # If media details request is NOT successful
        if media_details_response.status_code != 200:
            LOG.error(f'Received status code {media_details_response.status_code} from {url}\nResponse from api: {media_details_response_json}')
            return result

        LOG.info(f'Received status code {media_details_response.status_code} from {url}')
        
        # Add the selected media's title and plot to the result
        try:
            result['title'] = media_details_response_json['title']
            result['plot'] = media_details_response_json['synopsis']
        except KeyError as err:
            LOG.error(f'The recommended media was missing one of the following keys ["title", "synopsis"]\nrecommended media: {media_details_response_json}')
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

    # Request picture urls for this media
    try:
        url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/pictures'
        pictures_response = requests.get(url, timeout=(3,5))
    except requests.exceptions.Timeout as err:
        LOG.error(f'Timeout on {url}: {str(err)}')
        return result

    pictures_response_json = pictures_response.json()
    
    # If the request was NOT successful
    if pictures_response.status_code != 200:
        LOG.error(f'Received status code {pictures_response.status_code} from {url}\nResponse from api: {pictures_response_json}')
        return result
    
    LOG.info(f'Received status code {pictures_response.status_code} from {url}')

    # Array of urls for pictures of the selected media
    picture_urls = pictures_response_json['pictures']

    # If no picture urls were returned
    if len(picture_urls) == 0:
        LOG.info(f'No picture urls returned from {url}')
        return result
    
    # Select the index of a random picture url
    picture_index = randrange(len(picture_urls))
    
    # Save the file path for the picture of the selected media
    current_timestamp = int(time.time())
    picture_file_path = f'./images/{selected_media["mal_id"]}_{current_timestamp}.png'

    try:
        # Create a picture file
        image_file = open(picture_file_path, 'w')
        # Request the picture from the selected picture url
        # Save it to the picture_file_path
        urllib.request.urlretrieve(picture_urls[picture_index]['large'], picture_file_path)
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
