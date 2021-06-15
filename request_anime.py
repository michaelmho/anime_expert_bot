import os
import time
import json
import requests
import secrets
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def get_new_code_challenge():
    challenge = secrets.token_urlsafe(100)
    state = secrets.token_urlsafe(20)
    return challenge[:128], state[:24]

def get_new_auth_code():
    global CODE_CHALLENGE, CLIENT_ID, EMAIL, PASSWORD
    CODE_CHALLENGE, state = get_new_code_challenge()

    # Create authorize url
    base_url = "https://myanimelist.net/v1/oauth2/authorize"
    response_type = "code"
    url = f'{base_url}?response_type={response_type}&client_id={CLIENT_ID}&code_challenge={CODE_CHALLENGE}&state={state}'

    # Open url in chrome
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

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

    driver.implicitly_wait(5)

    # Hit allow button
    # This authoirizes this client to access the MAL account
    allowButton = driver.find_elements_by_xpath('//*[@id="content"]/div/div/div/form/input[2]')
    allowButton[0].click()
    
    # Wait for page to connect
    time.sleep(10)

    # Capture the redirect url
    final_url = driver.current_url
    # Exit the browser
    driver.quit()

    # Select the state and code parameters from the return url
    returned_parameters = final_url.split("code=")[1]
    returned_code, returned_state = returned_parameters.split("&state=")

    # If the returned state does NOT equal the sent state
    # Theres an issue return a blank code
    if state != returned_state:
        returned_code = ""

    return returned_code
    
def generate_new_token(grant_type, grant_value):
    # grant_types: 'refresh_token', 'authorization_code'
    global CLIENT_ID, CODE_CHALLENGE, AUTH_CODE

    if grant_type == "authorization_code" & AUTH_CODE == "":
        AUTH_CODE = get_new_auth_code()

    url = 'https://myanimelist.net/v1/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'code_verifier': CODE_CHALLENGE,
        'grant_type': grant_type,
        'code': grant_value
    }

    response = requests.post(url, data)
    response.close()
    print('Token generated successfully!')

    if response.status_code == 200:
        with open('token.json', 'w') as file:
            json.dump(response.json(), file, indent = 4)
            print('Token saved in "token.json"')

        return retrieve_token('access_token')
    else:
        print(f'error {response.status_code} while retrieving from {url}')
        return ""

def retrieve_token(token_type):
    global AUTH_CODE

    try:
        f = open('./token.json',)
    except IOError:
        if generate_new_token('authorization_code', AUTH_CODE) == "":
            return ""
        else:
           f = open('./token.json',) 

    token_data = json.load(f)
    return token_data[token_type]

def get_anime_with_genre(genre):
    url = f'https://api.myanimelist.net/v2/anime/ranking?ranking_type=airing&limit=10&genre=comedy'
    response = requests.get(url, headers={'Authorization': f'Bearer {retrieve_token("access_token")}'})
    
    if response.status_code == 401:
        response.close()
        generate_new_token('refresh_token', retrieve_token('refresh_token'))
        response = requests.get(url, headers={'Authorization': f'Bearer {retrieve_token("access_token")}'})
    
    if response.status_code != 200:
        print(f'error {response.status_code} while retrieving from {url}')
        result = ""
    else:
        result = response.json()

    response.close()
    print(result)
    return result

CLIENT_ID = os.environ['CLIENT_ID']
CODE_CHALLENGE = ""
EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']

if 'AUTH_CODE' not in os.environ:
    os.environ['AUTH_CODE'] = get_new_auth_code()
AUTH_CODE = os.environ['AUTH_CODE']

get_anime_with_genre('comedy')
