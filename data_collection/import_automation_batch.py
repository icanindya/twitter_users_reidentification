import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config

GOOGLE_USERNAME = ''
GOOGLE_PASSWORD = ''
TWITTER_USERNAME = ''
TWITTER_PASSWORD = ''


def twitter_login(driver):
    twt_uname = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[1]/input')
    twt_uname.send_keys(TWITTER_USERNAME)

    twt_pass = driver.find_element_by_xpath('//*[@id="page-container"]/div/div[1]/form/fieldset/div[2]/input')
    twt_pass.send_keys(TWITTER_PASSWORD + Keys.ENTER)


def twitter_launch_import(driver):
    driver.get('https://twitter.com/who_to_follow/import')
    twitter_login(driver)
    import_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="import-services-list"]/li[1]/button')))


def twitter_import_contacts(driver, file_path):
    driver.get('https://twitter.com/who_to_follow/import')

    import_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="import-services-list"]/li[1]/button')))
    import_button.click()

    # wait for Gmail oAuth window
    WebDriverWait(driver, 10).until(EC.new_window_is_opened)
    driver.switch_to.window(driver.window_handles[1])

    time.sleep(2)

    google_login(driver)

    allow_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'submit_approve_access')))
    allow_button.click()

    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
    driver.switch_to.window(driver.window_handles[0])

    contact_list = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, 'timeline')))

    actionchains = ActionChains(driver)
    actionchains.move_to_element_with_offset(contact_list, 0, 0).click().perform()

    not_end_reached = True

    while not_end_reached:
        actionchains.send_keys(Keys.PAGE_DOWN).perform()
        try:
            WebDriverWait(driver, 1).until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="timeline"]/div/div[2]/div[1]/div/div[1]/div/p[2]/button')))
            not_end_reached = False
        except:
            pass

    with open(file_path, 'w', encoding='utf-8') as wf:
        wf.write(driver.page_source)


def twitter_store_delete_contacts(driver, file_path):
    driver.get('https://twitter.com/settings/contacts_dashboard')

    try:
        pass_field = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "user_data_dashboard_auth_password")))
        pass_field.send_keys(TWITTER_PASSWORD + Keys.ENTER)
    except:
        pass

    actionchains = ActionChains(driver)

    not_end_reached = True

    while not_end_reached:
        actionchains.send_keys(Keys.PAGE_DOWN).perform()
        try:
            backtotop_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Back to top')]")))
            not_end_reached = False
            time.sleep(1)
            backtotop_button.click()
        except:
            pass

    with open(file_path, 'w', encoding='utf-8') as wf:
        wf.write(driver.page_source)

    del_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Remove all contacts']")))
    del_button.click()
    del_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Remove']")))
    del_button.click()


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


def google_launch_contacts(driver):
    driver.get('https://contacts.google.com/')
    google_login(driver)
    import_button1 = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Import contacts']]")))


def google_create_contact_list(driver, file_path):
    driver.get('https://contacts.google.com/')

    import_button1 = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Import contacts']]")))
    import_button1.click()

    file_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    file_input.send_keys(file_path)

    import_button2 = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//button[span[text()='Import']]")))
    import_button2.click()

    list_selecor = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Imported on')]")))


def google_del_contact_list(driver):
    list_label = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class='KIAioe'][tabindex='0']")))
    actionchains = ActionChains(driver)
    actionchains.move_to_element(list_label).click().perform()

    delete_icon = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][aria-label='Delete label']")))
    actionchains = ActionChains(driver)
    actionchains.move_to_element(delete_icon).click().perform()

    delete_checkbox = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='radio'][data-value='delete']")))
    actionchains = ActionChains(driver)
    actionchains.move_to_element(delete_checkbox).click().perform()

    actionchains = ActionChains(driver)
    actionchains.send_keys(Keys.TAB + Keys.TAB + Keys.ENTER).perform()

    WebDriverWait(driver, 20).until(EC.invisibility_of_element((By.CSS_SELECTOR, "a[class='KIAioe'][tabindex='0']")))


def start_less_granular():
    NUM_SPLITS = 2000

    options = Options()
    # options.add_argument('--headless')

    google_driver = webdriver.Chrome(config.SELENIUM_CHDVR_PATH, options=options)
    google_driver.set_window_position(1921, 0)
    google_driver.maximize_window()
    twitter_driver = webdriver.Chrome(config.SELENIUM_CHDVR_PATH, options=options)
    twitter_driver.maximize_window()

    google_launch_contacts(google_driver)
    twitter_launch_import(twitter_driver)

    try:
        print('Deleting Google Contacts.')
        google_del_contact_list(google_driver)
    except:
        pass

    try:
        print('Deleting Twitter Contacts.')
        twitter_delete_contacts(twitter_driver)
    except:
        pass

    i = -1
    while i < NUM_SPLITS - 1:
        i += 1
        try:
            if os.path.isfile(r'D:\Data\Linkage\FL\FL18\tw_imports_new\imp_{}.html'.format(i)):
                continue

            print('file {}'.format(i))

            con_file_path = r'D:\Data\Linkage\FL\FL18\fl_con_splits_new\con_{}.csv'.format(i)
            acc_file_path = r'D:\Data\Linkage\FL\FL18\tw_accounts_new\acc_{}.html'.format(i)
            imp_file_path = r'D:\Data\Linkage\FL\FL18\tw_imports_new\imp_{}.html'.format(i)

            google_create_contact_list(google_driver, con_file_path)
            twitter_import_contacts(twitter_driver, acc_file_path)
            google_del_contact_list(google_driver)
            twitter_store_delete_contacts(twitter_driver, imp_file_path)

        except Exception as e:
            print('Exception at file {}: {}'.format(i, str(e)))

            try:
                print('Deleting Google Contacts for Exception.')
                google_del_contact_list(google_driver)
            except:
                pass

            try:
                print('Deleting Twitter Contacts for Exception.')
                twitter_delete_contacts(twitter_driver)
            except:
                pass

            i -= 1


if __name__ == "__main__":
    start_less_granular()
