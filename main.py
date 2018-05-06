from bs4 import BeautifulSoup as bs4

import requests
import re

# TODO: MOVE HTTP/PARSE CODE TO SEPARATE MODULE
r = requests.get('http://www.presidency.ucsb.edu/ws/index.php?pid=119039')
soup = bs4(r.content, 'lxml')
text = soup.find('span', attrs={'class': 'displaytext'})
name_pattern = re.compile(r'(\S+)\s\((D|R)(\S+)?\)') # matches Schumer (D-NY)
debaters = {
    name_pattern.search(i).group(1).upper(): name_pattern.search(i).group(2)
    for i in text.find_all(string=name_pattern)
}
lines = text.find_all('p')
# HTTP/PARSE CODE end

current_debater = None
for line in lines:
    if line.b:
        speaker = line.b.string.strip(':')
        if speaker in debaters:
            current_debater = speaker
        else:
            current_debater = None
    if current_debater:
