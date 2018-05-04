from bs4 import BeautifulSoup as bs4
import requests
import re

r = requests.get('http://www.presidency.ucsb.edu/ws/index.php?pid=119039')

soup = bs4.soup(r.content, 'html.parser')

text = soup.find('span', attrs={'class': 'displaytext'})

name_pattern = re.compile(r'(\S+)\s\((D|R)(\S+)?\)')

for 
