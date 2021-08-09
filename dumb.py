import requests

token = '1bd1d493-abcf-4b51-9698-374ddb9f46bd'
#response = requests.get('https://api.heroku.com/apps/anime-expert-bot/config-vars', headers={'Accept':'application/vnd.heroku+json; version=3', 'Authorization':f'Bearer {token}'})
#print(response.json())
response = requests.patch('https://api.heroku.com/apps/anime-expert-bot/config-vars', headers={'Accept':'application/vnd.heroku+json; version=3', 'Authorization':f'Bearer {token}'}, data={'LAST_SEEN_ID':2222222223})
print(response.json())