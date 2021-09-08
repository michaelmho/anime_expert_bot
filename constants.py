import logging
import os as _os
import logging.handlers
import dotenv as _dotenv

_dotenv.load_dotenv()

logging.basicConfig(
    format='[%(levelname)s]\t%(asctime)s : %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename='./text_files/aeb.log',
            maxBytes=5*1024*1024,
            backupCount=2,
            encoding='utf-8',
            mode='a',
            delay=0
        )        
    ]
)
LOG = logging.getLogger(__name__)
GENRES = {
    'anime': {
        'action': '1',
        'adventure': '2',
        'cars': '3',
        'comedy': '4',
        'dementia': '5',
        'demons': '6',	
        'mystery': '7',
        'drama': '8',
        'ecchi': '9',	
        'fantasy': '10',	
        'game': '11',	
        'hentai': '12',	
        'historical': '13',
        'horror': '14',	
        'kids': '15',	
        'magic': '16',	
        'martial-arts': '17',
        'mecha': '18',	
        'music': '19',	
        'parody': '20',	
        'samurai': '21',	
        'romance': '22',	
        'school': '23',	
        'sci-fi': '24',	 
        'shoujo': '25',	
        'shoujo-ai': '26',
        'shounen': '27',	
        'shounen-ai': '28',
        'space': '29',
        'sports': '30',	
        'super-power': '31',
        'vampire': '32',	
        'yaoi': '33',	
        'yuri': '34',	
        'harem': '35',	
        'slice-of-life': '36',
        'supernatural': '37',
        'military': '38',
        'police': '39',		
        'psychological': '40',
        'thriller': '41',
        'seinen': '42',	
        'josei': '43'
    },
    'manga': {
        'action': '1',
        'adventure': '2',
        'cars': '3',
        'comedy': '4',
        'dementia': '5',
        'demons': '6',	
        'mystery': '7',
        'drama': '8',
        'ecchi': '9',	
        'fantasy': '10',	
        'game': '11',	
        'hentai': '12',	
        'historical': '13',
        'horror': '14',	
        'kids': '15',	
        'magic': '16',	
        'martial-arts': '17',
        'mecha': '18',	
        'music': '19',	
        'parody': '20',	
        'samurai': '21',	
        'romance': '22',	
        'school': '23',	
        'sci-fi': '24',	 
        'shoujo': '25',	
        'shoujo-ai': '26',
        'shounen': '27',	
        'shounen-ai': '28',
        'space': '29',
        'sports': '30',	
        'super-power': '31',
        'vampire': '32',	
        'yaoi': '33',	
        'yuri': '34',	
        'harem': '35',	
        'slice-of-life': '36',
        'supernatural': '37',
        'military': '38',
        'police': '39',		
        'psychological': '40',
        'seinen': '41',
        'josei': '42',	
        'doujinshi': '43',
        'gender-bender': '44',
        'thriller': '45'
    }
}
MEDIA_STATUSES = {
    'anime': 'airing',
    'manga': 'publishing'
}
MEDIA_TYPES = MEDIA_STATUSES.keys()
TOKEN = _os.environ['TOKEN']
API_KEY = _os.environ['API_KEY']
API_SECRET = _os.environ['API_SECRET']
ACCESS_KEY = _os.environ['ACCESS_KEY']
ACCESS_SECRET = _os.environ['ACCESS_SECRET']
