from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Helper function I found to convert the higher follower counts to decimal numbers
def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)

options = webdriver.FirefoxOptions()

# Comment/uncomment to show a live view
#options.set_headless()

username = input("Login to instagram\n\nEnter your username\n")
password = input("Enter your password\n")
fraud_user = input("Enter the user suspected of FRAUD\n")

driver = webdriver.Firefox(options=options)

# LOGIN PHASE
# ------------
driver.get('https://instagram.com/')
time.sleep(1)
user = driver.find_element_by_name('username')
user.clear()
user.send_keys(username)
pw = driver.find_element_by_name('password')
pw.clear() 
pw.send_keys(password)

found = False 
while (not found) :
    try:
        loginButton = driver.find_element_by_xpath('/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]')
        found = True
    except Exception as e:
        print("Element not found, retrying...")
        time.sleep(1)

loginButton.click()

# Logging in...
print("Logging in.")
time.sleep(1)
print(".")
time.sleep(1)
print(".")
time.sleep(1)

dismissButton = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button')
dismissButton.click()
time.sleep(1)

found = False
while (not found) :
    try:
        dismissButton = driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')
        found = True
    except Exception as e:
        print("Element not found, retrying...")
        time.sleep(1)

dismissButton.click()

# LOGGED IN
# -----------

# Search for fraud user
search_bar = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/input')
search_bar.clear()
search_bar.send_keys(fraud_user)
time.sleep(0.8)

found = driver.find_element_by_xpath('/html/body/div[1]/section/nav/div[2]/div/div/div[2]/div[3]/div[2]/div/a[1]/div/div[2]/div/span')
found.click()

# Load the fraud's page
time.sleep(1)

found = False
while (not found) :
    try:
        followers = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')
        found = True
    except Exception as e:
        print("Element not found, retrying...") # Page hasn't loaded fast enough
        time.sleep(1)

print(convert_str_to_number(followers.text))
followers.click()
time.sleep(0.7)

f_body = driver.find_element_by_xpath('//div[@class="isgrP"]')
scroll = 0
try:
    while (scroll < 30):
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', f_body)
        time.sleep(0.2)
        scroll += 1
except Exception as e:
    print(e)

#driver.close()

