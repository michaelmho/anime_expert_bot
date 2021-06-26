import json
import requests
import time
import logging
import urllib.request
from random import randrange
from urllib.error import HTTPError

log = logging.getLogger(__name__)


def api_request(params, result):
    # Request the top {limit} anime currently airing with the requested genre
    limit = 15
    url = f'https://api.jikan.moe/v3/search/{params["media_type"]}?page=1{params["status_query_param"]}{params["genre_query_param"]}&limit={limit}&order_by=score'
    response = requests.get(url)
    response_data = response.json()

    # If the request was NOT successful
    if response.status_code != 200:
        log.error(f'Received status code {response.status_code} from {url}\nResponse from api: {response_data}')
    else:
        log.info(f'Received status code {response.status_code} from {url}')

        # Index of the returned anime we will select
        anime_index = randrange(limit)
        # Json array of all anime returned
        returned_anime = response_data['results']

        # If any anime were returned
        if len(returned_anime) == 0:
            log.info(f'No anime returened from {url}')
        else:
            selected_anime = returned_anime[anime_index]
            current_timestamp = int(time.time())
            # Path for jpg to store the anime cover photo
            image_file_path = f'./images/{selected_anime["mal_id"]}_{current_timestamp}.jpg'

            try:
                # Open the image file, and save the jpg cover photo of the selected anime
                image_file = open(image_file_path, 'w')
                urllib.request.urlretrieve(selected_anime['image_url'], image_file_path)
                image_file.close()

                # Add the selected anime's info to the final result
                result['title'] = selected_anime['title']
                result['synopsis'] =  selected_anime['synopsis']
                result['image_file_path'] = image_file_path
            except IOError as err:
                log.error(f'Problem opening file {image_file_path}')
                log.error(str(err))
            except KeyError as err:
                log.error(f'The selected anime was missing one of the following keys ["title", "synopsis", "image_url"]\nselected anime: {selected_anime}')
                log.error(str(err))
            except HTTPError as err:
                log.error(f'Received status code {err.code} from "{selected_anime["image_url"]}"')
          
    return result
