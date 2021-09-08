import requests

from constants import LOG, TOKEN

# Not currently in use
def get_last_seen_id(file_name):
    try:
        f_read = open(file_name, "r")
        last_seen_id = int(f_read.read().strip())
        f_read.close()
    except ValueError:
        f_read.close()
        last_seen_id = 111111111
        set_last_seen_id(last_seen_id, file_name)
    except FileNotFoundError:
        last_seen_id = 111111111
        set_last_seen_id(last_seen_id, file_name)
    
    return last_seen_id


# Not currently in use
def set_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, "w")
    f_write.write(str(last_seen_id))
    f_write.close()
    return


def update_heroku_env_variable(key, value):
    LOG.info(' ')
    try:
        # Update {key} env variable through the heroku api
        body = {f'{key}':f'{value}'}
        url = 'https://api.heroku.com/apps/anime-expert-bot/config-vars'
        head = {'Accept':'application/vnd.heroku+json; version=3', 'Authorization':f'Bearer {TOKEN}'}
        response = requests.patch(url, headers=head, data=body)
        response.raise_for_status()

        # Validate {key} was updated
        if value != (response.json())[f'{key}']:
            raise requests.exceptions.RequestException(f'API failed to update {key}')
    except requests.exceptions.RequestException as err:
        LOG.error(f'Could not update {key}')
        LOG.error(str(err))
        exit()
    except KeyError as err:
        LOG.error(f'Could not update {key}')
        LOG.error(str(err))
        exit()
