import json
import requests
import time
import logging
import urllib.request
from random import randrange
from urllib.error import HTTPError

log = logging.getLogger(__name__)


def api_request(params, result):
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

        # Index of the returned media we will select
        media_index = randrange(limit)
        # Json array of all media returned
        returned_media = response_data['results']

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

                picture_urls = response_data['pictures']
                picture_index = randrange(len(picture_urls))
                current_timestamp = int(time.time())
                # Path for jpg to store the media picture
                image_file_path = f'./images/{selected_media["mal_id"]}_{current_timestamp}.jpg'

                try:
                    # Open the image file, and save the picture of the selected media
                    image_file = open(image_file_path, 'w')
                    urllib.request.urlretrieve(picture_urls[picture_index]["large"], image_file_path)
                    image_file.close()

                    # Add the selected media's info to the final result
                    result['title'] = selected_media['title']
                    result['synopsis'] =  selected_media['synopsis']
                    result['image_file_path'] = image_file_path
                except IOError as err:
                    log.error(f'Problem opening file {image_file_path}')
                    log.error(str(err))
                except KeyError as err:
                    log.error(f'The selected media was missing one of the following keys ["title", "synopsis", "image_url"]\nselected media: {selected_media}')
                    log.error(str(err))
                except HTTPError as err:
                    log.error(f'Received status code {err.code} from "{selected_media["image_url"]}"')
          
    return result

#api_request({'media_type' : 'anime','status_query_param' : '','genre_query_param' : ''}, {'title' : '','synopsis' : '','image_file_path' : ''})