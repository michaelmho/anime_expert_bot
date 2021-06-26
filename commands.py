import logging
from mal_api import api_request


def parse_mention(mention):
    result = {
        'title' : '',
        'synopsis' : '',
        'image_file_path' : ''
    }

    arguments = mention.strip().lower().split(' ')

    if len(arguments) < 3:
        log.info('Missing argument(s)')     
        return result

    try:
        parse_command = commands[arguments[1]]
    except KeyError:
        log.info(f'Command "{arguments[1]}" is not recognized')
        return result 
    
    return parse_command(arguments[1:], result)


def suggest(arguments, result):
    #   Command: Suggest
    #       Parameters
    #           Current
    #               Not required
    #               Indicates that only currently running series should be suggested
    #           Genre
    #               Not Required
    #               Genre of media to be returned, see Genre class for possible values
    #           media_type
    #               Required
    #               Type of media to be returned, possible values: 'anime' or 'manga'    
    #       Format
    #           @AnimeExpertBot suggest [current] <genre> <media_type>  

    argument_count = len(arguments)

    if not (arguments[-1] in media_statuses.keys()):
        log.info(f'Invalid media type "{arguments[-1]}"; expected "anime" or "manga"')
        return result

    request_params = {
        'media_type' : arguments[-1],
        'status_query_param' : '',
        'genre_query_param' : ''
    }

    if argument_count == 2:
        return api_request(request_params, result)

    arg_is_current = lambda arg : True if arg == 'current' else False
    get_status_query_param = lambda media_type : f'&staus={media_type}'

    arg_is_genre = lambda arg : True if arg in genres[arguments[-1]].keys() else False
    get_genre_query_param = lambda genre : f'&genre={genres[arguments[-1]][genre]}'
    
    if arg_is_current(arguments[1]):
        request_params['status_query_param'] = get_status_query_param(media_statuses[request_params['media_type']])

        if argument_count == 3:
            return api_request(request_params, result)
        else:
            possible_genre = ' '.join(arguments[2:-1])

            if arg_is_genre(possible_genre):
                request_params['genre_query_param'] = get_genre_query_param(possible_genre)
                return api_request(request_params, result)
            else:
                log.info(f'Invalid genre "{possible_genre}"')
                return result
    else:
        possible_genre = ' '.join(arguments[1:-1])

        if arg_is_genre(possible_genre):
            request_params['genre_query_param'] = get_genre_query_param(possible_genre)
            return api_request(request_params, result)
        else:
            log.info(f'Invalid genre "{possible_genre}"')
            return result


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
        'seinen': 41,
        'josei': 42,	
        'doujinshi': 43,
        'gender bender': 44,
        'thriller': 45
    }
}
media_statuses = {
    'anime': 'airing',
    'manga': 'publishing'
}
commands = {
    'suggest' : suggest
}