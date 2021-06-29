import json
import requests
import time
import logging
import urllib.request
from random import randrange
from urllib.error import HTTPError
from PIL import Image, ImageEnhance

log = logging.getLogger(__name__)


def mal_api_request(params):
    result = {
        'title' : '',
        'plot' : '',
        'image_file_path' : ''
    }

    # Request the top {limit} media with the requested genre
    limit = 50
    url = f'https://api.jikan.moe/v3/search/{params["media_type"]}?page=1{params["status_query_param"]}{params["genre_query_param"]}&limit={limit}&order_by=score'
    response = requests.get(url)
    response_data = response.json()

    # If the request was NOT successful
    if response.status_code != 200:
        log.error(f'Received status code {response.status_code} from {url}\nResponse from api: {response_data}')
    else:
        log.info(f'Received status code {response.status_code} from {url}')

        # Array of all media returned
        returned_media = response_data['results']
        # Index of the returned media we will select
        media_index = randrange(len(returned_media))

        if len(returned_media) == 0:
            log.info(f'No media returened from {url}')
        else:
            selected_media = returned_media[media_index]

            # Request pictures urls for this media
            url = f'https://api.jikan.moe/v3/{params["media_type"]}/{selected_media["mal_id"]}/pictures'
            response = requests.get(url)
            response_data = response.json()
            
            # If the request was NOT successful
            if response.status_code != 200:
                log.error(f'Received status code {response.status_code} from {url}\nResponse from api: {response_data}')
            else:
                log.info(f'Received status code {response.status_code} from {url}')

                # Select a random picture url
                picture_urls = response_data['pictures']
                picture_index = randrange(len(picture_urls))
                
                # File path for media picture
                current_timestamp = int(time.time())
                image_file_path = f'./images/{selected_media["mal_id"]}_{current_timestamp}.png'

                try:
                    # Open the picture file, and save the picture of the selected media
                    image_file = open(image_file_path, 'w')
                    urllib.request.urlretrieve(picture_urls[picture_index]["large"], image_file_path)
                    image_file.close()
                    
                    # Open image file and then resize and enhance using PIL 
                    image_file = Image.open(image_file_path)
                    resized_im = image_file.resize((round(image_file.size[0]*0.75), round(image_file.size[1]*0.75)))

                    enhancer = ImageEnhance.Sharpness(resized_im)

                    factor = 2
                    im_s_1 = enhancer.enhance(factor)
                    im_s_1.save(image_file_path, quality=100)
                    image_file.close()

                    # Add the selected media's info to the final result
                    result['title'] = selected_media['title']
                    result['plot'] =  selected_media['synopsis']
                    result['image_file_path'] = image_file_path
                except IOError as err:
                    log.error(f'Problem opening file {image_file_path}')
                    log.error(str(err))
                except KeyError as err:
                    log.error(f'The selected media was missing one of the following keys ["title", "synopsis"]\nselected media: {selected_media}')
                    log.error(str(err))
                except HTTPError as err:
                    log.error(f'Received status code {err.code} from "{selected_media["image_url"]}"')
          
    return result

#mal_api_request({'media_type' : 'anime','status_query_param' : '','genre_query_param' : ''}, {'title' : '','plot' : '','image_file_path' : ''})