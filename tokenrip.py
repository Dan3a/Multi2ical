from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import json

def login_and_get_session_storage(username, password, login_url, dashboard_url):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    target_url = "https://multi.univ-lorraine.fr/loginin?app=edt"
    driver.get(target_url)

    username_input = driver.find_element("id", "username")
    password_input = driver.find_element("id", "password")

    username_input.send_keys(username)
    password_input.send_keys(password)

    password_input.submit()

    sleep(2)


    session_storage_data = driver.execute_script("return JSON.stringify(sessionStorage);")

    driver.quit()

    return session_storage_data

username = "<NOM D'UTILISATEUR UL>"
password = f'<MOT DE PASSE UL>'
login_url = 'https://auth.univ-lorraine.fr/login?service=https://multi.univ-lorraine.fr/login'
dashboard_url = 'https://multi.univ-lorraine.fr/home'

session_storage_data = login_and_get_session_storage(username, password, login_url, dashboard_url)

session_storage_data = json.loads(session_storage_data)

refreshToken = session_storage_data['refreshToken']
token = session_storage_data['token']

with open('<OUTPUT PATH>', 'w') as f:
    data = [refreshToken, token]
    for line in data:
        f.write(line + "\n")
