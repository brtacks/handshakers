from bs4 import BeautifulSoup as bs4
from datetime import date

import requests
import re
import sys

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

PRESIDENTIAL = 'Presidential'
VICE_PRESIDENTIAL = 'Vice Presidential'
DEMOCRATIC = 'Democratic'
REPUBLICAN = 'Republican'

# Don't specify party; check for opposites.
PRESIDENTS_BY_YEAR = {
    2012: 'OBAMA',
    1996: 'BUSH',
    1984: 'REAGAN',
    1980: 'REAGAN',
    1976: 'FORD',
}

# TITLE's are the types of titles debaters are given in a transcript.
TITLE_A = 'bold'
TITLE_B = 'italics'
TITLE_C = 'regular'
TITLE_P = 'participants'

# Each title has a certain regex pattern.
TITLE_PATTERNS = {
    TITLE_A: r'(?i)(\w+):',
    TITLE_B: r'(?i)(\w+)\.',
    # TITLE_C pattern is left empty as there are two cases, both resolved within
    # the function in which TITLE_C is used.
    TITLE_C: '',
    TITLE_P: r'(\S+)\s\((D|R)(\S+)?\)'
}

DEBATERS_BY_YEAR = {
    2012: {
        PRESIDENTIAL: {
            'OBAMA': 'D',
            'ROMNEY': 'R',
            'pattern': TITLE_B,
        },
        VICE_PRESIDENTIAL: {
            'BIDEN': 'D',
            'RYAN': 'R',
            'pattern': TITLE_A,
        },
    },
    2008: {
        PRESIDENTIAL: {
            'OBAMA': 'D',
            'MCCAIN': 'R',
            'pattern': TITLE_A,
        },
        VICE_PRESIDENTIAL: {
            'BIDEN': 'D',
            'PALIN': 'R',
            'pattern': TITLE_A,
        },
    },
    2004: {
        PRESIDENTIAL: {
            'KERRY': 'D',
            'BUSH': 'R',
            'pattern': TITLE_B,
        },
        VICE_PRESIDENTIAL: {
            'EDWARDS': 'D',
            'CHENEY': 'R',
            'pattern': TITLE_C,
        },
        DEMOCRATIC: ['CLARK', 'LIEBERMAN', 'KUCINICH', 'DEAN', 'KERRY',
                     'SHARPTON', 'EDWARDS'],
    },
    2000: {
        PRESIDENTIAL: {
            'GORE': 'D',
            'BUSH': 'R',
            'pattern': TITLE_C,
        },
        VICE_PRESIDENTIAL: {
            'LIEBERMAN': 'D',
            'CHENEY': 'R',
            'pattern': TITLE_C,
        },
    },
    1996: {
        PRESIDENTIAL: {
            'CLINTON': 'D',
            'DOLE': 'R',
            'pattern': TITLE_B,
        },
        VICE_PRESIDENTIAL: {
            'GORE': 'D',
            'KEMP': 'R',
            'pattern': TITLE_C,
        },
    },
    1992: {
        PRESIDENTIAL: {
            'CLINTON': 'D',
            'BUSH': 'R',
            'pattern': TITLE_C,
        },
        VICE_PRESIDENTIAL: {
            'GORE': 'D',
            'QUAYLE': 'R',
            'pattern': TITLE_C,
        },
    },
    1988: {
        PRESIDENTIAL: {
            'DUKAKIS': 'D',
            'BUSH': 'R',
            'pattern': TITLE_C,
        },
        VICE_PRESIDENTIAL: {
            'BENTSEN': 'D',
            'QUAYLE': 'R',
            'pattern': TITLE_C,
        },
    },
    1984: {
        PRESIDENTIAL: {
            'MONDALE': 'D',
            'REAGAN': 'R',
            'pattern': TITLE_C,
        },
        VICE_PRESIDENTIAL: {
            'FERRARO': 'D',
            'BUSH': 'R',
            'pattern': TITLE_C,
        },
    },
    1980: {
        PRESIDENTIAL: {
            'CARTER': 'D',
            'REAGAN': 'R',
            'pattern': TITLE_C,
        },
    },
    1976: {
        PRESIDENTIAL: {
            'CARTER': 'D',
            'FORD': 'R',
            'pattern': TITLE_C,
        },
        VICE_PRESIDENTIAL: {
            'MONDALE': 'D',
            'DOLE': 'R',
            'pattern': TITLE_C,
        },
    },
    1960: {
        PRESIDENTIAL: {
            'KENNEDY': 'D',
            'NIXON': 'R',
            'pattern': TITLE_C,
        },
    },
}

def collect_transcripts():
    r = requests.get('http://www.presidency.ucsb.edu/debates.php')
    soup = bs4(r.content, 'lxml')
    docdate = soup.find('span', attrs={'class': 'docdate'})
    table = docdate.parent.table.table
    year = None
    for tr in table.find_all('tr'):
        year_label = tr.find('td', attrs={'class':'roman'})
        if year_label is not None:
            year = int(year_label.text)
        if tr.a:
            url = tr.a.attrs['href']
            create_transcript(url, year)

# create_transcript creates a transcript dictionary.
def create_transcript(url, year):
    soup = get_soup(url)
    transcript = init_transcript(soup, url)
    transcript['debaters'] = get_debaters(soup, transcript['debate_type'], year)
    print_transcript(transcript)

# get_debaters finds each candidate and every line they spoke.
def get_debaters(soup, debate_type, year):
    text = soup.find('span', attrs={'class': 'displaytext'})
    debaters = find_debaters(text, debate_type, year)
    if len(debaters) == 0:
        return debaters
    lines = text.find_all('p')

    current_debater = None
    for line in lines:
        if DEBATERS_BY_YEAR[year][DEBATE_TYPE]
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

# The format of debate transcript varies by year and debate type (presidential
# or primary).
def find_debaters(text, debate_type, year):
    debaters = {}
    for i in text.children:
        debater = line_debater(i.text, debate_type, year)
        if debater:
            debaters[debater] = {
                'lines': [],
                'party': DEBATERS_BY_YEAR[year][debate_type][debater]
            }
    return debaters

# line_debater finds the debater name in a string.
def line_debater(line, debate_type, year):
    pattern_title = DEBATERS_BY_YEAR[year][debate_type]['pattern']
    pattern = TITLE_PATTERNS[pattern_title]
    if pattern != TITLE_C:
        match = re.search(pattern, line)
    else:
        if ':' in line:
            comps = line.split(':')[0].split(' ')
            if len(comps) > 0:
                match = re.search(r'^[A-Z]:$', comps[0])
                if match:
                    return match.group(1)
    if match.group(1) == 'President':
        return PRESIDENTS_BY_YEAR[year]

def init_transcript(soup, url):
    date = soup.find('span', attrs={'class': 'docdate'})
    date = get_date_from_str(date.text)
    papers_title = soup.find('span', attrs={'class': 'paperstitle'}).text
    debate_type = None
    if 'Vice' in papers_title:
        debate_type = VICE_PRESIDENTIAL
    ELif 'Democratic' in papers_title:
        debate_type = DEMOCRATIC
    elif 'Republican' in papers_title:
        debate_type = REPUBLICAN
    elif 'Presidential' in papers_title:
        debate_type = PRESIDENTIAL

    if debate_type is None or date is None:
        raise ValueError(
            "Could not get date and debate_type from debate with at %s." % url
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

def get_soup(url):
    r = requests.get(url)
    return bs4(r.content, 'lxml')

def print_transcript(t):
    print "== %s Debate, %s =====" % (t['debate_type'], str(t['date']))
    print "PARTICIPANTS:"
    for name, v in t['debaters'].items():
        print "  %s (%s)" % (name, v['party'])
        print "\n"

if __name__ == '__main__':
    collect_transcripts()
