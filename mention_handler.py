import re
from constants import GENRES, MEDIA_STATUSES


def parse_mention(mention):
    # Parameters
    #    Classic
    #        Not required
    #        Indicates that only media started between 1988 and 1998 should be returned
    #    Current
    #        Not required
    #        Indicates that only currently running media should be suggested
    #    Genre
    #        Required
    #        Genre of media to be returned, see Genre class for possible values
    #    media_type
    #        Not Required
    #        Type of media to be returned, possible values: 'anime' or 'manga'    
    # Format
    #    @AnimeExpertBot (current | classic) <genre> <media_type> 

    help_message = ''
    mal_request_params = {
        'query' : '',
        'genre_ids' : '',
        'is_classic' : False,
        'is_current' : False,
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
        help_message = 'Missing argument(s)'
        return help_message, mal_request_params

    if 'like' in arguments:
        help_message, mal_request_params['query'], mal_request_params['media_type'] = parse_mention_with_like(arguments)
        return help_message, mal_request_params

    # Validator for each argument type
    arg_is_current = lambda arg : True if arg == 'current' else False
    arg_is_classic = lambda arg : True if arg == 'classic' else False
    arg_is_media_type = lambda arg: True if arg in MEDIA_STATUSES.keys() else False
    arg_is_genre = lambda arg : True if arg in GENRES[mal_request_params['media_type']].keys() else False
    validators = [arg_is_genre, arg_is_classic, arg_is_current, arg_is_media_type]

    get_genre_id = lambda arg : GENRES[mal_request_params["media_type"]][arg]

    # Used to track which arguments have already been found
    max_genres = 4
    genres_found = 0
    media_type_found = False

    # Try to find a media type and remove it from the arguments
    try:
        arguments.remove('manga')
        mal_request_params['media_type'] = 'manga'
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
        for arg_is_x in validators:
            if arg_is_x(argument):
                is_valid_argument = True
                break
        
        if is_valid_argument:
            # If this argument is a genre
            if arg_is_x == arg_is_genre:
                genres_found += 1

                if genres_found > max_genres:
                    help_message = f'Only {max_genres} genres are allowed in a request'
                    break
                
                # If this is the first genre found
                if genres_found == 1:
                    mal_request_params['genre_ids'] = f'{get_genre_id(argument)}'
                # Else, append this genre id to genre_ids 
                else:
                    genre_id = get_genre_id(argument)
                    if not(genre_id in mal_request_params['genre_ids']):
                        mal_request_params['genre_ids'] += f',{genre_id}'
                    else:
                        genres_found-=1
            # If this argument is current
            elif arg_is_x == arg_is_current:
                # If current has NOT been found
                if not mal_request_params['is_current']:
                    # If classic has NOT been found
                    if not mal_request_params['is_classic']:
                        mal_request_params['is_current'] = True
                    elif not help_message:
                        help_message = 'Found both "current" and "classic"'
            # If this argument is classic
            elif arg_is_x == arg_is_classic:
                # If classic has NOT been found
                if not mal_request_params['is_classic']:
                    # If current has NOT been found
                    if not mal_request_params['is_current']:
                        mal_request_params['is_classic'] = True
                    elif not help_message:
                        help_message = 'Found both "current" and "classic"'
            # If this argument is a media type
            else:
                # If a media type has already been found
                if media_type_found:
                    # If this argument does not match the previously found media type
                    if not (argument == mal_request_params['media_type']):
                        help_message = 'Found both "manga" and "anime"'
                        break
                else:
                    mal_request_params['media_type'] = argument
                    media_type_found = True
            
            # Remove this argument from the array
            del arguments[arg_index]
            arg_index -= 1
        # Invalid argument passed
        else:
            help_message = f'"{argument}" is not recognized'
            break

        # Move to the next argument
        arg_index += 1       

    return help_message, mal_request_params


def parse_mention_with_like(arguments):
    query = ''
    help_message = ''
    media_type = 'anime'
    
    if arguments[0] == 'like':
        if len(arguments) > 1:
            query = ' '.join(arguments[1:])
        else:
            help_message = 'Missing argument(s)'
    elif arguments[1] == 'like':
        if arguments[0] == 'manga':
            media_type = 'manga'
            if len(arguments) > 2:
                query = ' '.join(arguments[2:])
            else:
                help_message = 'Missing argument(s)'
        else:
            help_message = f'Command "{arguments[0]} {arguments[1]}" is not recognized'
    else:
        help_message = '"like" or "manga like" can only be used at the beginning of a request'            

    return help_message, query, media_type


def get_reply_text(help_message, media_info):
    if help_message:
        help_message_text = f'There\'s a problem with your request: {help_message}\nBut maybe you\'ll like this\n'
    else:
        help_message_text = ''

    if media_info['title'] and media_info['plot']:
        media_info_text = f'Title: {media_info["title"]}\nPlot: {media_info["plot"]}'
    else:
        media_info_text = 'Sorry, I encountered a problem while getting your suggestion'
    
    reply_text = help_message_text + media_info_text
    if len(reply_text) > 275:
        reply_text = reply_text[0:272] + '...'
    
    return reply_text
