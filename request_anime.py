import json
import requests
from random import randrange
import urllib.request

genres = {
    'action': 1,
    'adventure': 2,
    'cars': 3,
    'comedy': 4,
    'dementia': 5,
    'demons': 6,	
    'mystery': 7,
    'drama': 8,
    'ecchi': 9,	
    'fantasy': 10,	
    'game': 11,	
    'hentai': 12,	
    'historical': 13,
    'horror': 14,	
    'kids': 15,	
    'magic': 16,	
    'martial arts': 17,
    'mecha': 18,	
    'music': 19,	
    'parody': 20,	
    'samurai': 21,	
    'romance': 22,	
    'school': 23,	
    'sci fi': 24,	 
    'shoujo': 25,	
    'shoujo ai': 26,
    'shounen': 27,	
    'shounen ai': 28,
    'space': 29,
    'sports': 30,	
    'super power': 31,
    'vampire': 32,	
    'yaoi': 33,	
    'yuri': 34,	
    'harem': 35,	
    'slice of life': 36,
    'supernatural': 37,
    'military': 38,
    'police': 39,		
    'psychological': 40,
    'thriller': 41,
    'seinen': 42,	
    'josei': 43
}


def get_anime_with_genre(requested_genre):
    final_result = {
        'successful': True,
    }

    # Format the requested genre
    requested_genre = (requested_genre.lower()).strip()

    # Try to save the id of the requested genre
    try: 
        genre_id = genres[requested_genre]
    except KeyError:
        # Error Logging
        print(f'Error in get_anime_with_genre(): requested genre "{requested_genre}" does not exist')
        if final_result['successful']: final_result['successful'] = False
        return final_result

    # Request the top {limit} anime currently airing with the requested genre
    media_type = 'anime'
    media_status = 'airing'
    limit = 10
    url = f'https://api.jikan.moe/v3/search/{media_type}?page=1&status={media_status}&genre={genre_id}&limit={limit}&order_by=score'
    response = requests.get(url)
    response_data = response.json()

    # If the request was NOT successful
    if response.status_code != 200:
        # Error Logging
        print(f'Error in get_anime_with_genre(): received status code {response.status_code} from {url}')
        print(f'Response from api: {response_data}')
        if final_result['successful']: final_result['successful'] = False
    else:
        # Index of the returned anime we will select
        anime_index = randrange(limit)
        # Json array of all animes returned
        returned_anime = response_data['results']

        # If no anime were returned
        if len(returned_anime) == 0:
            # Error logging
            print(f'Error in get_anime_with_genre(): no anime returned from {url}')
            if final_result['successful']: final_result['successful'] = False
        # Else, 1+ anime was/were returned
        else:
            selected_anime = returned_anime[anime_index]
            # Path for jpg to store the anime cover photo
            image_file_path = f'./images/{selected_anime["mal_id"]}.jpg'

            try:
                # Open the image file, and save the jpg cover photo of the selected anime
                image_file = open(image_file_path, 'w')
                urllib.request.urlretrieve(selected_anime['image_url'], image_file_path)
                image_file.close()

                # Add the selected anime's info to the final result
                final_result['title'] = selected_anime['title']
                final_result['synopsis'] =  selected_anime['synopsis']
                final_result['image_file_path'] = image_file_path
            except IOError as err:
                # Error logging
                print(f'Error in get_anime_with_genre(): could not open file {image_file_path}')
                print(str(err))
                if final_result['successful']: final_result['successful'] = False
            except KeyError as err:
                # Error logging
                print(f'Error in get_anime_with_genre(): the selected anime was missing one of the following keys ["title", "synopsis", "image_url"]')
                print(str(err))
                if final_result['successful']: final_result['successful'] = False
            
    return final_result
