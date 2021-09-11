import re

from constants import GENRES, MEDIA_STATUSES, MEDIA_TYPES, LOG

class MentionAnalyzer():
    def __init__(self):
        self.validators = [self.validate_classic, self.validate_current, self.validate_genre, self.validate_media_type]
        self.reset()

    def reset(self):
        # Control variables
        self.max_genres = 4
        self.genres_found = 0
        self.media_type_found = False

        # Return values
        self.query = ''
        self.genre_ids = ''
        self.help_message = ''
        self.is_classic = False
        self.is_current = False
        self.media_type = 'anime'

        # Array of all words in the mention
        self.arguments = []

    
    def analyze(self, mention_text):
        LOG.info(f'> Analyzing "{mention_text}"')
        self.parse_mention(mention_text)

        if len(self.arguments) == 0:
            self.help_message = 'Missing argument(s)'
        elif 'like' in self.arguments:
            self.analyze_mention_with_like()
        else:
            self.analyze_mention()

        results = self.help_message, {    
            'query' : self.query,
            'genre_ids' : self.genre_ids,
            'is_classic' : self.is_classic,
            'is_current' : self.is_current,
            'media_type' : self.media_type
        }

        self.reset()

        LOG.info(f'help_message: \'{results[0]}\'')
        LOG.info(f'search_criteria: {results[1]}')
        return results


    def parse_mention(self, mention_text):
        # Create arguments array from mention text
        self.arguments = mention_text.lower().strip().split(' ')
        # Remove '@AnimeExpertBot' from the arguments
        self.arguments.remove('@animeexpertbot')
        # Remove any characters that are not a-z or '-' from each argument
        self.arguments = list(map(lambda argument : re.sub('[^a-z-]', '', argument), self.arguments))
        # Remove any arguments that are now ''
        self.arguments = [argument for argument in self.arguments if argument != '']


    def validate_genre(self, argument):
        arg_is_genre = True if argument in GENRES[self.media_type].keys() else False

        if arg_is_genre:
            self.genres_found += 1

            if self.genres_found <= self.max_genres:                
                # If this is the first genre found
                if self.genres_found == 1:
                    self.genre_ids = f'{GENRES[self.media_type][argument]}'
                # Else, append this genre id to self.genre_ids 
                else:
                    genre_id = GENRES[self.media_type][argument]
                    if not(genre_id in self.genre_ids):
                        self.genre_ids += f',{genre_id}'
                    else:
                        self.genres_found-=1
            elif not self.help_message:
                self.help_message = f'Only {self.max_genres} genres are allowed in a request'

        return arg_is_genre


    def validate_current(self, argument):
        arg_is_current = True if argument == 'current' else False

        if arg_is_current:
            # If current has NOT been found
            if not self.is_current:
                # If classic has NOT been found
                if not self.is_classic:
                    self.is_current = True
                elif not self.help_message:
                    self.help_message = 'Found both "current" and "classic"'

        return arg_is_current


    def validate_classic(self, argument):
        arg_is_classic = True if argument == 'classic' else False

        if arg_is_classic:
            # If classic has NOT been found
            if not self.is_classic:
                # If current has NOT been found
                if not self.is_current:
                    self.is_classic = True
                elif not self.help_message:
                    self.help_message = 'Found both "current" and "classic"'

        return arg_is_classic


    def validate_media_type(self, argument):
        arg_is_media_type = True if argument in MEDIA_TYPES else False

        if arg_is_media_type:
            if argument == 'manga' and not self.media_type_found:
                self.media_type = 'manga'

            if self.media_type_found and not self.help_message:
                self.help_message = 'You used "manga" and "anime"'

        return arg_is_media_type


    def analyze_mention_with_like(self):
        if self.arguments[0] == 'like':
            if len(self.arguments) > 1:
                self.query = ' '.join(self.arguments[1:])
            else:
                self.help_message = 'There\'s nothing after "like"'
        elif self.arguments[1] == 'like':
            if self.arguments[0] in MEDIA_TYPES:
                self.media_type = self.arguments[0]
                if len(self.arguments) > 2:
                    self.query = ' '.join(self.arguments[2:])
                else:
                    self.help_message = 'There\'s nothing after "like"'
            else:
                self.help_message = f'"{self.arguments[0]} like" is not recognized'
        else:
            self.help_message = '"like" should be at the beginning'


    def analyze_mention(self):
        for argument in self.arguments:
            valid_argument = False
            for validator in self.validators:
                valid_argument = validator(argument)
                if valid_argument:
                    break

            if not valid_argument:
                if not self.help_message:
                    self.help_message = f'"{argument}" is not recognized'
                break

