from lxml import html
import re
import requests 

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

user = input("Enter the instagram user to fetch\n")
url = 'https://www.instagram.com/' + str(user)
page = requests.get(url)
tree = html.fromstring(page.content)

# Get the path to the 'meta' tag named 'description' which contains the counts
data = tree.xpath('//meta[@name="description"]')

# The string containing the followers, following, and number of posts
metaValues = data[0].values()
metaContent = metaValues[0]

# Strip all commas
metaContent = metaContent.replace(',','')

# Create an array of the 3 values: FollowerCount, FollowingCount, PostCount
values = [str(s) for s in metaContent.split()]
values = [values[0], values[2], values[4]]
for x in range(3):
    values[x] = convert_str_to_number(values[x])

print("Account [" + str.upper(user) + "] has " + str(values[0]) + " followers, follows " + str(values[1]) + " people, has " + str(values[2]) + " posts\n")


# url = 'https://www.instagram.com/' + str(user) + '/followers/'
# page = requests.get(url)
# tree = html.fromstring(page.content)

# TODO: Use Selenium to scrape the dynamic 'followers' list 
# FOR EACH of the followers, GET their follower count
# <div class="isgrP" /> contains the popup + the scrollbar
# <div class ="PZuss" /> contains the list of followers
# <a class="FPmhX notranslate _0imsa " title="followerUserName" /> contains each follower's name

# print(dir(followers[0]))
# ['__bool__', '__class__', '__contains__', '__copy__', '__deepcopy__', '__delattr__', '__delitem__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__',
#  '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__', '__setattr__', 
#  '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_init', 'addnext', 'addprevious', 'append', 'attrib', 'base', 'base_url', 'body', 'classes', 'clear', 'cssselect', 'drop_tag', 
#  'drop_tree', 'extend', 'find', 'find_class', 'find_rel_links', 'findall', 'findtext', 'forms', 'get', 'get_element_by_id', 'getchildren', 'getiterator', 'getnext', 'getparent', 'getprevious', 'getroottree', 
#  'head', 'index', 'insert', 'items', 'iter', 'iterancestors', 'iterchildren', 'iterdescendants', 'iterfind', 'iterlinks', 'itersiblings', 'itertext', 'keys', 'label',
#  'make_links_absolute', 'makeelement', 'nsmap', 'prefix', 'remove', 'replace', 'resolve_base_href', 'rewrite_links', 'set', 'sourceline', 'tag', 'tail', 'text', 'text_content', 'values', 'xpath']
