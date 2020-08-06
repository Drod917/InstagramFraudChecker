# Daniel Rodriguez 08/04/2020

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import utils
from getpass import getpass

username = input("Login to instagram\n\nEnter your username: ")
password = getpass(prompt="Enter your password: ")
fraud_user = input("Enter the user suspected of FRAUD: \n")

options = webdriver.FirefoxOptions()
# Set to true for a live view
options.headless = False
driver = webdriver.Firefox(options=options)


# LOGIN PHASE
# ------------
print("Retrieving instagram.com . . .")
driver.get('https://instagram.com/')
time.sleep(1) # Allow IG to load

# Enter login information
found = False 
while (not found) :
    try:
        user = driver.find_element_by_name('username')
        pw = driver.find_element_by_name('password')
        found = True
    except Exception as e:
        print("Username\PW boxes not found, retrying...")
        time.sleep(1)
user.clear()
user.send_keys(username)
pw.clear() 
pw.send_keys(password)

found = False 
while (not found) :
    try:
        loginButton = driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div')
        found = True
    except Exception as e:
        print("Login button not found, retrying...")
        time.sleep(1)
loginButton.click()

# Give 3 seconds for the server to complete the login
print("Logging in ", end="", flush=True)
for x in range(3):
    time.sleep(1)
    print(". ", end="", flush=True)
print()

# Logged in, dismiss popups
found = False
while (not found) :
    try:
        dismissButton = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button')
        found = True
    except Exception as e:
        print("1st dismiss button not found, retrying...")
        time.sleep(1)
dismissButton.click()
time.sleep(1) # Prepare for 2nd popup

found = False
while (not found) :
    try:
        dismissButton = driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')
        found = True
    except Exception as e:
        print("2nd dismiss button not found, retrying...")
        time.sleep(1)
dismissButton.click()

# LOGGED IN
# -----------

# Search for fraud user
search_bar = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/input')
search_bar.clear()
search_bar.send_keys(fraud_user)
time.sleep(0.8) # Allow search to execute

found = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div[2]/div/a[1]/div/div[2]/div/span')
found.click()

time.sleep(1) # Allow fraud's page to load

# Grab followers
found = False
while (not found) :
    try:
        followers = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')
        found = True
    except Exception as e:
        print("Followers element not found, retrying...") # Page hasn't loaded fast enough
        time.sleep(1)

followerCount = followers.text.replace(',','') # Strip all commas
print(fraud_user + " has " + str(utils.convert_str_to_number(followerCount)) + " followers.\n")
followers.click()
time.sleep(0.7) # Allow popup to load

# Scroll through followers list to load all followers
found = False
while (not found) :
    try:
        f_body = driver.find_element_by_xpath('//div[@class="isgrP"]') # Element to push down
        track_height = driver.find_element_by_xpath('//div[@class="PZuss"]') # Element that gets extended on dynamic load
        found = True
    except Exception as e:
        print("Dynamic list not found, retrying...") # Page hasn't loaded fast enough
        time.sleep(1)

# Scroll through the follower list to generate a complete file
height = track_height.size['height'] # initial height
print("Initial height: " + str(height) + "px\n")
changed = True
try:
    while (changed):
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', f_body) # load next
        time.sleep(0.2)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', f_body) # move down
        print("track_height after execute_script: " + str(track_height.size['height']))
        if (height == track_height.size['height']):
            print("Waiting for more followers to load...\n")
            time.sleep(5)
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', f_body) # move down
            if (height == track_height.size['height']):
                changed = False
        height = track_height.size['height']
except Exception as e:
    print(e)
print("End of followers reached")

followers_found = 0
names_list = driver.find_elements_by_css_selector('a.FPmhX.notranslate._0imsa')
names_file = open('names.txt', 'w')
for account in names_list:
    names_file.write(account.text + str('\n'))
    followers_found += 1

names_file.write('Followers found: ' + str(followers_found) + '\n')
names_file.close()
driver.close()

# <div class="                    Igw0E     IwRSH        YBx95       _4EzTm                                                                                                               _9qQ0O ZUqME" style="height: 32px; width: 32px;"><svg aria-label="Loading..." class="  By4nA" viewBox="0 0 100 100"><rect fill="#555555" height="6" opacity="0" rx="3" ry="3" transform="rotate(-90 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.08333333333333333" rx="3" ry="3" transform="rotate(-60 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.16666666666666666" rx="3" ry="3" transform="rotate(-30 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.25" rx="3" ry="3" transform="rotate(0 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.3333333333333333" rx="3" ry="3" transform="rotate(30 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.4166666666666667" rx="3" ry="3" transform="rotate(60 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.5" rx="3" ry="3" transform="rotate(90 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.5833333333333334" rx="3" ry="3" transform="rotate(120 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.6666666666666666" rx="3" ry="3" transform="rotate(150 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.75" rx="3" ry="3" transform="rotate(180 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.8333333333333334" rx="3" ry="3" transform="rotate(210 50 50)" width="25" x="72" y="47"></rect><rect fill="#555555" height="6" opacity="0.9166666666666666" rx="3" ry="3" transform="rotate(240 50 50)" width="25" x="72" y="47"></rect></svg></div>
# <svg class=" By4nA" aria-label="Loading..." viewBox="0 0 100 100" /> IS THE LOADING SYMBOL WHEN SCROLLING DOWN