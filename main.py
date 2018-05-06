from bs4 import BeautifulSoup as bs4
from datetime import date

import requests
import re

# The general pattern matches participants' names in general debates.
general_pattern = re.compile(r'(\S+)\s\((D|R)(\S+)?\)')

# The party pattern matches participants' names in party debates.
party_pattern = re.compile(r'')

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

PRESIDENTIAL = 'Presidential'
DEMOCRATIC = 'Democratic'
REPUBLICAN = 'Republican'

TITLE_PATTERNS = {
    PRESIDENTIAL: re.compile(r'(\S+)\s\((D|R)(\S+)?\)'),
    DEMOCRATIC: re.compile(r'(\w+)((\s\([\w\s]+\))|;)'),
    REPUBLICAN: re.compile(r'(\w+)((\s\([\w\s]+\))|;)'),
}

def collect_transcripts():
    r = requests.get('http://www.presidency.ucsb.edu/debates.php')
    soup = bs4(r.content, 'lxml')
    docdate = soup.find('span', attrs={'class': 'docdate'})
    table = docdate.parent.table.table
    for tr in table.find_all('tr'):
        if tr.a:
            url = tr.a.attrs['href']
            create_transcript(url)

# create_transcript creates a transcript dictionary.
def create_transcript(url):
    soup = get_soup(url)
    transcript = init_transcript(soup, url)
    transcript['debaters'] = get_debaters(soup, transcript['debate_type'])
    print_transcript(transcript)

# get_debaters finds each candidate and every line they spoke.
def get_debaters(soup, debate_type):
    text = soup.find('span', attrs={'class': 'displaytext'})
    title_pattern = TITLE_PATTERNS[debate_type]
    debaters = {}
    for i in text.children:
        if i.name == 'p':
            break
        line = str(i)
        match = title_pattern.search(line)
        if match:
            debaters[match.group(1).upper()] = {
                'lines': [0],
                'party': match.group(2) if debate_type == PRESIDENTIAL
                else debate_type[0]
            }
    if len(debaters) == 0:
        return debaters
    lines = text.find_all('p')

    current_debater = None
    for line in lines:
        if line.b:
            speaker = line.b.text.strip(':')
            if speaker in debaters:
                current_debater = speaker
            else:
                current_debater = None
        if current_debater:
            if line.b:
                clean_text = line.text.replace(line.b.text, '')
            else:
                clean_text = line.text
                clean_text = clean_text.strip()
                debaters[current_debater]['lines'].append(clean_text)

    return debaters

def init_transcript(soup, pid):
    date = soup.find('span', attrs={'class': 'docdate'})
    date = get_date_from_str(date.text)
    papers_title = soup.find('span', attrs={'class': 'paperstitle'}).text
    debate_type = None
    if 'Democratic' in papers_title:
        debate_type = DEMOCRATIC
    elif 'Republican' in papers_title:
        debate_type = REPUBLICAN
    elif 'Presidential' in papers_title:
        debate_type = PRESIDENTIAL

    if debate_type is None or date is None:
        raise ValueError(
            "Could not get date and debate_type from debate with PID %d." % pid
        )
    return {
        'date': date,
        'debate_type': debate_type,
    }

def get_date_from_str(str):
    date_components = re.findall(r"[\w']+", str)
    if len(date_components) != 3:
        raise ValueError("Unable to get date from string %s." % str)
    month = MONTHS.index(date_components[0])
    if month == -1:
        raise ValueError(
            "Month %s in string %s is incorrect." % (date_components[0], str)
        )
    return date(
        int(date_components[2]), # year
        month + 1,
        int(date_components[1]), # day
    )

def get_soup_from_pid(pid):
    r = requests.get('http://www.presidency.ucsb.edu/ws/index.php?pid=%d' % pid)
    return bs4(r.content, 'lxml')

def print_transcript(transcript):
    print "== % Debate, % =====" (t['debate_type'], str(t['date']))
    print "PARTICIPANTS:"
    for name, v in transcript['debaters'].items():
        print "  %s (%s)" % (name, v['party'])
    print "\n"

if __name__ == '__main__':
    create_transcript(76223)
