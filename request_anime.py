import os
import time
import json
import requests
import secrets
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

cred_file = open("./text_files/credentials.json", "r")
CREDENTIALS = json.loads(cred_file.read())
cred_file.close()

CLIENT_ID = CREDENTIALS['CLIENT_ID']
EMAIL = CREDENTIALS['EMAIL']
PASSWORD = CREDENTIALS['PASSWORD']
AUTH_CODE = ""
CODE_CHALLENGE = ""

def get_new_code_challenge_and_state():
    challenge = secrets.token_urlsafe(100)
    state = secrets.token_urlsafe(20)
    return challenge[:128], state[:24]

def get_new_auth_code():
    global CODE_CHALLENGE, CLIENT_ID, EMAIL, PASSWORD

    # Create authorize url
    CODE_CHALLENGE, state = get_new_code_challenge_and_state()
    base_url = "https://myanimelist.net/v1/oauth2/authorize"
    response_type = "code"
    url = f'{base_url}?response_type={response_type}&client_id={CLIENT_ID}&code_challenge={CODE_CHALLENGE}&state={state}'

    # Open url in chrome
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    # Wait for page to load
    driver.implicitly_wait(5)

    # Choose to login with google
    loginWithGoogle = driver.find_element_by_xpath('//*[@id="content"]/div/section[1]/div/div[1]/a[1]')
    loginWithGoogle.click()

    # Input email
    emailBox = driver.find_element_by_xpath('//*[@id ="identifierId"]')
    emailBox.send_keys(EMAIL)

    # Hit next
    nextButton = driver.find_elements_by_xpath('//*[@id ="identifierNext"]')
    nextButton[0].click()
  
    # Input password
    passWordBox = driver.find_element_by_xpath('//*[@id ="password"]/div[1]/div / div[1]/input')
    passWordBox.send_keys(PASSWORD)
  
    # Hit next
    nextButton = driver.find_elements_by_xpath('//*[@id ="passwordNext"]')
    nextButton[0].click()

    # Wait for page to load
    driver.implicitly_wait(5)

    # Hit allow button
    # This authoirizes this client to access the MAL account
    allowButton = driver.find_elements_by_xpath('//*[@id="content"]/div/div/div/form/input[2]')
    allowButton[0].click()
    
    # Wait for page to connect
    time.sleep(7)

    # Capture the redirect url
    final_url = driver.current_url
    # Exit the browser
    driver.quit()

    # Select the code and state parameters from the redirect url
    returned_parameters = final_url.split("code=")[1]
    returned_code, returned_state = returned_parameters.split("&state=")

    # If the returned state does NOT equal the sent state
    # There's an issue return a blank code
    if state != returned_state:
        returned_code = ""

    return returned_code
    
def generate_new_tokens(grant_type, grant_value):
    # grant_types: 'refresh_token', 'code'
    global CLIENT_ID, CODE_CHALLENGE, AUTH_CODE

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'grant_type': grant_type
    }

    if grant_type == 'authorization_code':
        # If the authorization code is blank
        # Try to generate a new one
        if grant_value == '':
            AUTH_CODE = get_new_auth_code()

        data['code_verifier'] = CODE_CHALLENGE
        data['code'] = AUTH_CODE
    else:
        data[grant_type] = grant_value

    response = requests.post(url, data)
    response.close()

    # If the token request was successful
    if response.status_code == 200:
        # Write the response to 'mal_tokens.json'
        with open('./text_files/mal_tokens.json', 'w') as file:
            json.dump(response.json(), file, indent = 4)
            print('Tokens saved in "mal_tokens.json"')

        return "Success"
    else:
        print(f'error {response.status_code}:{response.json()} while retrieving from {url} with {data}')
        return ""

def retrieve_token(token_type):
    global AUTH_CODE

    try:
        f = open('./text_files/mal_tokens.json',)
    # If 'mal_tokens.json' fails to open
    except IOError:
        # Try to generate new tokens
        if generate_new_tokens('authorization_code', AUTH_CODE) != "":
            f = open('./text_files/mal_tokens.json',)           
        else:
            return ""
    
    token_data = json.load(f)
    result = token_data[token_type]
    f.close()
    return result

def get_anime_with_genre(genre):
    url = f'https://api.myanimelist.net/v2/anime/ranking?ranking_type=airing&limit=10&genre=comedy'
    response = requests.get(url, headers={'Authorization': f'Bearer {retrieve_token("access_token")}'})
    
    # If the request is unathorized
    # Try to generate new tokens
    if response.status_code == 401:
        response.close()
        generate_new_tokens('refresh_token', retrieve_token('refresh_token'))
        response = requests.get(url, headers={'Authorization': f'Bearer {retrieve_token("access_token")}'})
    
    # If the request is successful
    if response.status_code == 200:
        result = response.json()
    else:
        print(f'error {response.status_code}:{response.json()} while retrieving from {url}')
        result = ""

    response.close()
    print(result)
    return result

get_anime_with_genre('comedy')
