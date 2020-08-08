# %%
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from getpass import getpass
from selenium.common.exceptions import ElementClickInterceptedException
import time
import utils

class FraudChecker():
    # Initialize the checker & login
    def __init__(self, username, password):
        print("Initializing...")
        options = webdriver.FirefoxOptions()
        options.headless = False # False for live view
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, 10)
        self.driver = driver 
        self.wait = wait
        print("Retrieving instagram.com...")
        driver.get('https://instagram.com/')

        # LOGIN PHASE
        # ------------
        print("Logging in...")
        wait.until(EC.element_to_be_clickable((By.NAME, 'username')))
        wait.until(EC.element_to_be_clickable((By.NAME, 'password')))
        user = driver.find_element_by_name('username')
        pw = driver.find_element_by_name('password')
        user.clear()
        user.send_keys(username)
        pw.clear()
        pw.send_keys(password)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, 
            '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div')))
        login_button = driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div')
        login_button.click()

        # Wait for 1st dismiss prompt
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/section/main/div/div/div/div/button')))
        dismiss_button = driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/div/div/div/button')
        dismiss_button.click()

        # Wait for 2nd dismiss prompt
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]')))
        dismiss_button = driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/div/div[3]/button[2]')
        dismiss_button.click()
        print("Logged in.")

    def check_for_fraud(self, fraud_user):   
        driver = self.driver 
        wait = self.wait

        # Search for fraud user
        search_bar = driver.find_element_by_xpath(
            '/html/body/div[1]/section/nav/div[2]/div/div/div[2]/input')
        search_bar.clear()
        search_bar.send_keys(fraud_user)
        print("Searching...")

        # Allow search to execute
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div[2]/div/a[1]/div/div[2]/div/span')))
        found = driver.find_element_by_xpath(
            '/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div[2]/div/a[1]/div/div[2]/div/span')
        found.click()

        # Allow fraud's page to load
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')))
        followers = driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')
        print("POTENTIAL FRAUD FOUND")

        # Grab followers
        follower_count = followers.text.replace(',','') # Strip all commas
        follower_count = utils.convert_str_to_number(follower_count)
        print(fraud_user + " has " + str(follower_count) + " followers.\n")

        try:
            followers.click()
        except ElementClickInterceptedException as e: # Popup closing, retry
            print("NotClickable error, retrying")
            time.sleep(0.5)
            followers = driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')
            followers.click()

        # Allow popup to load
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@class="isgrP"]')))
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@class="PZuss"]')))
        f_body = driver.find_element_by_xpath(
            '//div[@class="isgrP"]') # Element to push down
        track_height = driver.find_element_by_xpath(
            '//div[@class="PZuss"]') # Dynamically loaded element
        start = time.time()

        # Scroll through followers list to load all followers
        print("Loading " + str(fraud_user) + "'s followers...")
        height = track_height.size['height'] # Initial height
        done = False
        try:
            while (not done):
                driver.execute_script(
                    # load next
                    'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                    f_body)
                time.sleep(0.1) # Allow new elements to load
                driver.execute_script(
                    # move down
                    'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                    f_body)
                if (height == track_height.size['height']): # List didn't refresh, check for end
                    fetched_followers = len(driver.find_elements_by_css_selector(
                        'a.FPmhX.notranslate._0imsa'))
                    if (fetched_followers >= follower_count): # END AROUND THE COUNT INSTEAD
                        done = True
                    print(str(fetched_followers) + " followers loaded")
                    time.sleep(0.2)
                height = track_height.size['height']
        except Exception as e:
            print(e)
        end = time.time()

        # Retrieve the loaded list of names
        names_list = driver.find_elements_by_css_selector('a.FPmhX.notranslate._0imsa')
        followers_found = len(names_list)
        print("End of followers reached")
        print("Found " + str(followers_found) + " followers in " + str(end - start) + "s")
        self.names_list = names_list
        self.followers_found = followers_found

    def write_followers(self):
        names_list = self.names_list 
        followers_found = self.followers_found 
        driver = self.driver

        # Scroll through the follower list to generate a complete file
        with open('names.txt', 'w') as names_file:
            for account in names_list:
                names_file.write(account.text + str('\n'))
            names_file.write('Followers found: ' + str(followers_found) + '\n')
            names_file.close()
        print("File written")

        # Dismiss follower popup to prepare for subsequent searches
        try:
            dismiss = driver.find_element_by_xpath(
                '/html/body/div[4]/div/div/div[1]/div/div[2]/button')
            dismiss.click()
        except: # No prompt found
            pass
