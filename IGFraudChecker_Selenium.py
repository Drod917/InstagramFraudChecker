# Daniel Rodriguez 08/04/2020
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

username = input("Login to instagram\n\nEnter your username: ")
password = getpass(prompt="Enter your password: ")

options = webdriver.FirefoxOptions()
# Set to true for a live view
options.headless = True
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)

# LOGIN PHASE
# ------------
print("Retrieving instagram.com . . .")
driver.get('https://instagram.com/')

print("Logging in...")
# Enter login information
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

wait.until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/div[1]/section/main/div/div/div/div/button')))
dismiss_button = driver.find_element_by_xpath(
    '/html/body/div[1]/section/main/div/div/div/div/button')
dismiss_button.click()

wait.until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]')))
dismiss_button = driver.find_element_by_xpath(
    '/html/body/div[4]/div/div/div/div[3]/button[2]')
dismiss_button.click()

print("Logged in.")
# %%
# LOGGED IN
# -----------

fraud_user = input("Enter the user suspected of FRAUD: \n")

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
height = track_height.size['height'] # initial height
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
            if (fetched_followers == follower_count):
                done = True
            print(str(fetched_followers) + " followers loaded")
            time.sleep(0.2)
        height = track_height.size['height']
except Exception as e:
    print(e)
end = time.time()
names_list = driver.find_elements_by_css_selector('a.FPmhX.notranslate._0imsa')
followers_found = len(names_list)

print("End of followers reached")
print("Found " + str(followers_found) + " followers in " + str(end - start) + "s")

# Scroll through the follower list to generate a complete file
with open('names.txt', 'w') as names_file:
    for account in names_list:
        names_file.write(account.text + str('\n'))
    names_file.write('Followers found: ' + str(followers_found) + '\n')
    names_file.close()
print("File written")

# Dismiss follower popup to prepare for subsequent searches
dismiss = driver.find_element_by_xpath(
    '/html/body/div[4]/div/div/div[1]/div/div[2]/button')
dismiss.click()

# %%
driver.close()
# <div class="                    Igw0E     IwRSH        YBx95       _4EzTm                                                                                                               _9qQ0O ZUqME" style="height: 32px; width: 32px;"><svg aria-label="Loading..." class="  By4nA" viewBox="0 0 100 100"><rect fill="#555555" height="6" opacity="0" rx="3" ry="3" transform="rotate(-90 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.08333333333333333" rx="3" ry="3" transform="rotate(-60 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.16666666666666666" rx="3" ry="3" transform="rotate(-30 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.25" rx="3" ry="3" transform="rotate(0 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.3333333333333333" rx="3" ry="3" transform="rotate(30 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.4166666666666667" rx="3" ry="3" transform="rotate(60 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.5" rx="3" ry="3" transform="rotate(90 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.5833333333333334" rx="3" ry="3" transform="rotate(120 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.6666666666666666" rx="3" ry="3" transform="rotate(150 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.75" rx="3" ry="3" transform="rotate(180 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.8333333333333334" rx="3" ry="3" transform="rotate(210 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.9166666666666666" rx="3" ry="3" transform="rotate(240 50 50)" width="25" x="72" y="47"></rect></svg></div>
# <svg class=" By4nA" aria-label="Loading..." viewBox="0 0 100 100" /> IS THE LOADING SYMBOL WHEN SCROLLING DOWN

