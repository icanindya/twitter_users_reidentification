import linkedin_credentials as lcred
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config
import helper


def linkedin_login(driver):
    driver.get('https://www.linkedin.com/login')

    lnk_uname = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'username')))
    lnk_uname.send_keys(lcred.USERNAME)

    lnk_pword = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'password')))
    lnk_pword.send_keys(lcred.PASSWORD + Keys.ENTER)


def store_linkedin_profile(col, json):
    col.insert_one(json)


options = Options()
# options.add_argument('--headless')

driver = webdriver.Chrome(config.SELENIUM_CHDVR_PATH, options=options)
driver.maximize_window()
linkedin_login(driver)

with open(config.HTTPREQ_JS_PATH, 'r') as rf:
    js_func = ''.join(rf.readlines())

mongo_client = helper.get_mongo_client()

twitter_db = mongo_client['twitter']
voters_col = twitter_db['voters']
ground_truths_col = twitter_db['ground_truths']
lin_profiles_col = twitter_db['linkedin_profiles']

count = 0

for i, gt in enumerate(ground_truths_col.find({})):

    voter = voters_col.find_one({'serial': gt['voter_serial']})

    if not lin_profiles_col.find_one({'voter_serial': gt['voter_serial']}):

        url = 'https://www.linkedin.com/sales/gmail/profile/proxy/{}'.format(voter['email'])

        http_response = driver.execute_script('{}\nreturn makeHttpGetRequest("{}");'.format(js_func, url))

        if http_response['status'] == 200 or http_response['status'] == 400:

            if 'maximum click-through limit' in http_response['response_text']:
                raise Exception('Error: limit exceeded')

            if http_response['status'] == 200:
                count += 1
                print('call: {}, index: {}, email: {}'.format(count, i, voter['email']))
            else:
                print('call: {}, index: {}, email: {}'.format(count, i, voter['email']))

            json = {}
            json['voter_serial'] = gt['voter_serial']
            json['email'] = voter['email']
            json['status'] = http_response['status']
            json['response_text'] = http_response['response_text']

            store_linkedin_profile(lin_profiles_col, json)

        else:

            raise Exception('Error {}: {}'.format(http_response['status'], http_response['response_text']))
