import logging
import re


def parse_mention(mention):
    # Parameters
    #    Current
    #        Not required
    #        Indicates that only currently running series should be suggested
    #    Genre
    #        Not Required
    #        Genre of media to be returned, see Genre class for possible values
    #    media_type
    #        Not Required
    #        Type of media to be returned, possible values: 'anime' or 'manga'    
    # Format
    #    @AnimeExpertBot [current] <genre> <media_type> 

    message = ''
    mal_api_request_params = {
        'genre_query_param' : '',
        'status_query_param' : '',
        'media_type' : 'anime'
    }

    # Create arguments array from mention text
    arguments = mention.lower().strip().split(' ')
    # Remove '@AnimeExperBot' from the arguments
    del arguments[0]
    # Remove any characters that are not a-z or '-' from each argument
    arguments = list(map(lambda arg : re.sub('[^a-z-]', '', arg), arguments))
    # Remove any arguments that are now ''
    arguments = [arg for arg in arguments if arg != '']
    
    if len(arguments) == 0:
        message = 'Missing argument(s)'
        return message, mal_api_request_params

    # Validator for each argument type
    arg_is_genre = lambda arg : True if arg in genres[mal_api_request_params['media_type']].keys() else False
    arg_is_current = lambda arg : True if arg == 'current' else False
    arg_is_media_type = lambda arg: True if arg in media_statuses.keys() else False

    validators = [arg_is_genre, arg_is_current, arg_is_media_type]
    
    # Constructs query params for mal api request
    get_genre_query_param = lambda genre : f'&genre={genres[mal_api_request_params["media_type"]][genre]}'
    get_status_query_param = lambda : f'&staus={media_statuses[mal_api_request_params["media_type"]]}'

    # Control varibles for each argument type
    max_genres = 4
    genres_found = 0
    current_found = False
    media_type_found = False

    # Try to find a media type and remove it from the arguments
    try:
        arguments.remove('manga')
        mal_api_request_params['media_type'] = 'manga'
        media_type_found = True
    except ValueError:
        try:
            arguments.remove('anime')
            media_type_found = True
        except:
            pass

    # Loop through the rest of the arguments
    arg_index = 0
    while(len(arguments) > 0):
        # Try to validate this argument
        argument = arguments[arg_index]
        is_valid_argument = False
        for validator in validators:
            if validator(argument):
                is_valid_argument = True
                break
        
        if is_valid_argument:
            # If this argument is a genre
            if validator == arg_is_genre:
                genres_found += 1

                if genres_found > max_genres:
                    message = f'Only {max_genres} genres are allowed in a request'
                    break
                
                # If this is the first genre found
                if genres_found == 1:
                    mal_api_request_params['genre_query_param'] = get_genre_query_param(argument)
                # Else, add this genre id to genre_query_param 
                else:
                    if not(argument in mal_api_request_params['genre_query_param']):
                        mal_api_request_params['genre_query_param'] += f',{genres[mal_api_request_params["media_type"]][argument]}'
                    else:
                        genres_found-=1
            # If this argument is current
            elif validator == arg_is_current:
                # If current has already been found
                if current_found:
                    message = f'Found more than one "current"'
                    break
                else:
                    mal_api_request_params['status_query_param'] = get_status_query_param()
                    current_found = True
            # If this argument is a media type
            else:
                # If a media type has already been found
                if media_type_found:
                    media_type = mal_api_request_params["media_type"]
                    if media_type == argument:
                        message = f'Found more than one "{media_type}"'
                    else:
                        message = 'Found both "manga" and "anime"'
                    break
                else:
                    mal_api_request_params["media_type"] = argument
                    media_type_found = True
            
            # Remove this argument
            del arguments[arg_index]
            arg_index -= 1
        else:
            message = f'"{argument}" is not recognized'
            break

        arg_index += 1

    
    # if len(arguments) > 0:
    #     mal_api_request_params['genre_query_param'] = ''
    #     mal_api_request_params['status_query_param'] = ''        

    return message, mal_api_request_params


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


log = logging.getLogger(__name__)
genres = {
    'anime': {
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
        'martial-arts': 17,
        'mecha': 18,	
        'music': 19,	
        'parody': 20,	
        'samurai': 21,	
        'romance': 22,	
        'school': 23,	
        'sci-fi': 24,	 
        'shoujo': 25,	
        'shoujo-ai': 26,
        'shounen': 27,	
        'shounen-ai': 28,
        'space': 29,
        'sports': 30,	
        'super-power': 31,
        'vampire': 32,	
        'yaoi': 33,	
        'yuri': 34,	
        'harem': 35,	
        'slice-of-life': 36,
        'supernatural': 37,
        'military': 38,
        'police': 39,		
        'psychological': 40,
        'thriller': 41,
        'seinen': 42,	
        'josei': 43
    },
    'manga': {
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
        'martial-arts': 17,
        'mecha': 18,	
        'music': 19,	
        'parody': 20,	
        'samurai': 21,	
        'romance': 22,	
        'school': 23,	
        'sci-fi': 24,	 
        'shoujo': 25,	
        'shoujo-ai': 26,
        'shounen': 27,	
        'shounen-ai': 28,
        'space': 29,
        'sports': 30,	
        'super-power': 31,
        'vampire': 32,	
        'yaoi': 33,	
        'yuri': 34,	
        'harem': 35,	
        'slice-of-life': 36,
        'supernatural': 37,
        'military': 38,
        'police': 39,		
        'psychological': 40,
        'seinen': 41,
        'josei': 42,	
        'doujinshi': 43,
        'gender-bender': 44,
        'thriller': 45
    }
}
media_statuses = {
    'anime': 'airing',
    'manga': 'publishing'
}

#parse_mention('@AnimeExpertBot sci-fi comedy hentai action adventure')