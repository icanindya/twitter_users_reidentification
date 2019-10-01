import math
import os
import re
import sys
import time

import google_credentials as gcred
from bs4 import BeautifulSoup
from contactsapiclient import ContactsApiClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

GOOGLE_USERNAME = ''
GOOGLE_PASSWORD = ''
TWITTER_USERNAME = ''
TWITTER_PASSWORD = ''

TW_RUNNING_RECORDS_DIR = r"D:\Data\Linkage\FL\FL18\tw_running_records_new"
MASTER_GROUND_TRUTHS_DIR = r"D:\Data\Linkage\FL\FL18\master_ground_truths"

ACCOUNT_INDEX = None


def parse_account(page_source):
    soup = BeautifulSoup(page_source, 'lxml')

    match = soup.find('div', class_='content')

    profile = match.a
    bio = match.p

    if profile and bio:
        user_id = profile.get('data-user-id')
        profile_handle = profile.get('href')[1:]

        name_text = profile.strong.text
        name_text = re.sub(r'[^\x00-\x7F]+', ' ', name_text)
        name = re.sub(r'\s+', ' ', name_text).strip()

        tweets_public = 'F' if profile.find('span', text='Protected Tweets') else 'T'

        bio_text = bio.text
        bio_text = re.sub(r'[^\x00-\x7F]+', ' ', bio_text)
        biography = re.sub(r'\s+', ' ', bio_text).strip()

        return [name, profile_handle, user_id, tweets_public, biography]


def twitter_login(driver):
    twt_uname = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[1]/input')
    twt_uname.send_keys(TWITTER_USERNAME)

    twt_pass = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[2]/input')
    twt_pass.send_keys(TWITTER_PASSWORD + Keys.ENTER)


def twitter_launch_import(driver):
    driver.get('https://twitter.com/who_to_follow/import')
    twitter_login(driver)
    driver.get('https://twitter.com/i/optout')
    time.sleep(2)


#    driver.get('https://twitter.com/who_to_follow/import')
#    import_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="import-services-list"]/li[1]/button')))


def twitter_import_contacts(driver):
    driver.get('https://twitter.com/who_to_follow/import')

    import_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="import-services-list"]/li[1]/button')))
    import_button.click()

    # wait for Gmail oAuth window
    WebDriverWait(driver, 10).until(EC.new_window_is_opened)
    driver.switch_to.window(driver.window_handles[1])

    time.sleep(2)

    google_login(driver)

    allow_button = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.ID, 'submit_approve_access')))
    allow_button.click()

    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
    driver.switch_to.window(driver.window_handles[0])

    timeline = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'timeline')))
    header = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'content-main-heading')))

    if 'Gmail contacts' in header.text:
        #    print('header located: {}'.format(success_header.text))
        return parse_account(driver.page_source)
    else:
        return None


def twitter_delete_contacts(driver):
    driver.get('https://twitter.com/settings/contacts_dashboard')

    try:
        pass_field = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "user_data_dashboard_auth_password")))
        pass_field.send_keys(TWITTER_PASSWORD + Keys.ENTER)
    except:
        pass
    try:
        del_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Remove all contacts']")))
        del_button.click()
        del_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Remove']")))
        del_button.click()
    except:
        pass


def google_login(driver):
    try:
        acc_select = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, 'profileIdentifier')))
        acc_select.click()
    except:
        gog_uname = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'identifierId')))
        gog_uname.send_keys(GOOGLE_USERNAME + Keys.ENTER)
        gog_pass = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, 'password')))
        gog_pass.send_keys(GOOGLE_PASSWORD + Keys.ENTER)


def clean_twitter_google(twitter_driver, gc_client):
    error = True
    while error:
        try:
            twitter_delete_contacts(twitter_driver)
            gc_client.delete_all_contacts()
            error = False
        except:
            print('error in clearing twitter and google.')
            pass


def upload_individual(twitter_driver, gc_client, file_indexes):
    clean_twitter_google(twitter_driver, gc_client)

    for i in file_indexes:

        read_file_path = os.path.join(TW_RUNNING_RECORDS_DIR, "tw_running_rec_{}.txt".format(i))
        write_file_path = os.path.join(MASTER_GROUND_TRUTHS_DIR, 'master_ground_truths_{}.txt'.format(i))

        already_read = 0

        if os.path.isfile(write_file_path):
            with open(write_file_path, 'r') as rf:
                for line in rf:
                    if ':' in line:
                        already_read += 1

        line_num = 0

        with open(read_file_path, "r") as rf:

            with open(write_file_path, 'a') as wf:

                prev_contact_twitter_id = None

                for line in rf:
                    line_num += 1

                    if line_num <= already_read:
                        continue

                    error = True

                    while error:
                        try:
                            tokens = list(map(lambda x: x.strip(), line.split("\t")))
                            full_name = tokens[0]
                            email = tokens[1]

                            print('account: {}, file: {}, line: {}'.format(ACCOUNT_INDEX, i, line_num))

                            gc_client.create_contact("", "", full_name, email, "")
                            contact = twitter_import_contacts(twitter_driver)

                            if contact:
                                if contact[2] == prev_contact_twitter_id:
                                    raise Exception('previous contact not deleted!')
                                else:
                                    wf.write('{}:\t'.format(line_num) + '\t'.join(contact) + '\n')
                                    prev_contact_twitter_id = contact[2]
                            else:
                                wf.write('{}:\t'.format(line_num) + '\n')

                            error = False
                        except Exception as e:
                            print(e)
                        finally:
                            wf.flush()
                            clean_twitter_google(twitter_driver, gc_client)


def distribute_tasks(account_index):
    begin_file_index = 0
    end_file_index = 2000

    num_accounts = len(gcred.accounts)

    start = begin_file_index + account_index * int(math.ceil((end_file_index - begin_file_index + 1) / num_accounts))
    stop = min(end_file_index + 1, begin_file_index + (account_index + 1) * int(
        math.ceil((end_file_index - begin_file_index + 1) / num_accounts)))

    file_indexes = list(range(start, stop))

    global GOOGLE_USERNAME, GOOGLE_PASSWORD, TWITTER_USERNAME, TWITTER_PASSWORD, ACCOUNT_INDEX

    GOOGLE_USERNAME = gcred.accounts[account_index]
    GOOGLE_PASSWORD = gcred.password

    TWITTER_USERNAME = '{}@gmail.com'.format(GOOGLE_USERNAME)
    TWITTER_PASSWORD = gcred.password

    ACCOUNT_INDEX = account_index

    STORAGE_DIR = r'D:\Data\Linkage\FL\FL18\auth_tokens'
    storage_path = os.path.join(STORAGE_DIR, '{}.auth'.format(GOOGLE_USERNAME))
    gc_client = ContactsApiClient(gcred.client_ids[GOOGLE_USERNAME], gcred.client_secrets[GOOGLE_USERNAME],
                                  storage_path)

    options = Options()
    # options.add_argument('--headless')

    twitter_driver = webdriver.Chrome(config.SELENIUM_CHDVR_PATH, options=options)
    twitter_driver.maximize_window()
    twitter_launch_import(twitter_driver)

    upload_individual(twitter_driver, gc_client, file_indexes)


if __name__ == "__main__":
    distribute_tasks(int(sys.argv[1]))
