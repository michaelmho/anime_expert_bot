import json
import time
import requests
import urllib.request
from random import randrange
from urllib.error import HTTPError
from PIL import Image, ImageEnhance

from constants import MEDIA_STATUSES, LOG

class SuggestionRetriever:
    def __init__(self):
        self.api_url = 'https://api.jikan.moe/v3'
        self.reset()


    def reset(self):
        # Search criteria
        self.query = ''
        self.genre_ids = ''
        self.media_type = ''
        self.is_classic = False
        self.is_current = False

        # Return values
        self.plot = ''
        self.title = ''
        self.picture_file_path = ''

        # id of selected media
        self.media_id = ''
    

    def get_suggestion(self, search_criteria):
        LOG.info(f'> Retrieving suggestion')

        self.query = search_criteria['query']
        self.genre_ids = search_criteria['genre_ids']
        self.is_classic = search_criteria['is_classic']
        self.is_current = search_criteria['is_current']
        self.media_type = search_criteria['media_type']

        # If this is a request with like
        if self.query:
            self.get_similar_media()
        else:
            self.get_media_with_genre()

        if self.plot and self.title:
            self.save_media_picture()

        results = {'title' : self.title, 'picture_file_path' : self.picture_file_path, 'plot' : self.plot}

        self.reset()

        LOG.info(f'media_info: {results}')
        return results


    def mal_api_request(self, url, key):
        try:
            response = requests.get(url, timeout=(5,10))
        except requests.exceptions.Timeout as err:
            LOG.error(f'Timeout on {url}: {str(err)}')
            return []

        if response.status_code != 200:
            LOG.error(f'Received status code {response.status_code} from {url}\nApi response: {response.json()}')
            return []

        LOG.info(f'Received status code {response.status_code} from {url}')

        if key:
            try:
                results = (response.json())[key]
            except KeyError as err:
                LOG.error(f'Response missing key \"{key}\"')
                return []        

            if len(results) == 0:
                LOG.info(f'No results returned from {url}')
        else:
            results = response.json()

        return results


    def get_similar_media(self):
        # Form url to search for {self.media_type} with name like {self.query}
        encoded_query = urllib.parse.quote(self.query)
        url = f'{self.api_url}/search/{self.media_type}?page=1&q={encoded_query}'

        # Make the search request
        returned_media = self.mal_api_request(url, 'results')
        
        if returned_media:
            # Select the first returned media since it's the closest match
            media_id = returned_media[0]['mal_id']

            # Make a request for recommendations similar to the selected media
            url = f'{self.api_url}/{self.media_type}/{media_id}/recommendations'
            returned_recommendations = self.mal_api_request(url, 'recommendations')
            
            if returned_recommendations:
                # Select a random recommended media
                reccomendation_index = randrange(len(returned_recommendations))
                self.media_id = returned_recommendations[reccomendation_index]['mal_id']

                # Make a request for details on the selected media        
                url = f'{self.api_url}/{self.media_type}/{self.media_id}'
                returned_media_details = self.mal_api_request(url, '')
                
                if returned_media_details:
                    try:
                        self.title = returned_media_details['title']
                        self.plot = returned_media_details['synopsis']
                    except KeyError as err:
                        LOG.error(f'Recommended media: {returned_media_details}')
                        LOG.error(f'Response missing key \"{str(err)}\"')


    def get_media_with_genre(self):
        # Form url to search for the top {limit} media with the requested genre(s)
        limit = 50
        genre = f'&genre={self.genre_ids}' if self.genre_ids else ''
        status = f'&status={MEDIA_STATUSES[self.media_type]}' if self.is_current else ''
        start_end = f'&start_date=1988-00-00&end_date=1998-00-00' if self.is_classic else ''
        url = f'{self.api_url}/search/{self.media_type}?page=1{status}{genre}{start_end}&limit={limit}&order_by=score'

        # Make the search request
        returned_media = self.mal_api_request(url, 'results')
        
        if returned_media:
            # Select 1 of the returned media at random
            media_index = randrange(len(returned_media))
            selected_media = returned_media[media_index]

            try:
                self.title = selected_media['title']
                self.plot =  selected_media['synopsis']
                self.media_id = selected_media['mal_id']
            except KeyError as err:
                LOG.error(f'Selected media: {selected_media}')
                LOG.error(f'Response missing key \"{str(err)}\"')  


    def save_media_picture(self):
        # Request picture urls for the selected media
        url = f'{self.api_url}/{self.media_type}/{self.media_id}/pictures'
        returned_picture_urls = self.mal_api_request(url, 'pictures')
        
        if returned_picture_urls:
            # Select a random picture url
            picture_index = randrange(len(returned_picture_urls))
            selected_picture_url = returned_picture_urls[picture_index]['large']
            
            # Set the file path for the picture of the selected media
            current_timestamp = int(time.time())
            self.picture_file_path = f'./images/{self.media_id}_{current_timestamp}.png'

            try:
                # Request the picture of the selected media from the selected picture url
                # Save it to the picture file path
                picture_file = open(self.picture_file_path, 'w')
                urllib.request.urlretrieve(selected_picture_url, self.picture_file_path)
                picture_file.close()
                
                # Enhance the picture quality using PIL 
                picture_file = Image.open(self.picture_file_path)
                enhancer = ImageEnhance.Sharpness(picture_file)   
                enhancer = enhancer.enhance(2)
                enhancer.save(self.picture_file_path, quality=95)
            except IOError as err:
                self.picture_file_path = ''
                LOG.error(f'Problem opening file {self.picture_file_path}')
                LOG.error(str(err))
            except HTTPError as err:
                self.picture_file_path = ''
                LOG.error(f'Received status code {err.code} from "{selected_picture_url}"')

