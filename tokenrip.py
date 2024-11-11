from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import json

def login_and_get_session_storage(username, password, login_url, dashboard_url):
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    target_url = "https://mobile.univ-lorraine.fr/auth"
    driver.get(target_url)

    sleep(1)

    username_input = driver.find_element(By.CSS_SELECTOR, "ion-input[formcontrolname='username']")
    password_input = driver.find_element(By.CSS_SELECTOR, "ion-input[formcontrolname='password']")

    username_input = username_input.find_element(By.TAG_NAME, "input")
    password_input = password_input.find_element(By.TAG_NAME, "input")
    

    username_input.send_keys(username)
    password_input.send_keys(password)

    password_input.submit()

    sleep(1)


    session_storage_data = driver.execute_script("return JSON.stringify(localStorage);")

    driver.quit()

    return session_storage_data

username = "<NOM D'UTILISATEUR UL>"
password = f'<MOT DE PASSE UL>'
login_url = 'https://mobile.univ-lorraine.fr/auth'
dashboard_url = 'https://mobile.univ-lorraine.fr/features/widgets'

session_storage_data = login_and_get_session_storage(username, password, login_url, dashboard_url)

session_storage_data = json.loads(session_storage_data)

token = session_storage_data['cap_sec_auth-token']

with open('<TOKEN OUTPUT PATH>', 'w') as f:
    data = token
    f.write(data + "\n")
