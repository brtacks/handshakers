from bs4 import BeautifulSoup as bs4

import requests
import re

r = requests.get('http://www.presidency.ucsb.edu/ws/index.php?pid=119039')

soup = bs4(r.content, 'lxml')

text = soup.find('span', attrs={'class': 'displaytext'})

# Matches Schumer (D-NY)
name_pattern = re.compile(r'(\S+)\s\((D|R)(\S+)?\)')

participants = [
    (name_pattern.search(i).group(1).upper(), name_pattern.search(i).group(2))
    for i in text.find_all(string=name_pattern)
]

print participants
