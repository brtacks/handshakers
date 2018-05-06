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
VICE_PRESIDENTIAL = 'Vice Presidential'
DEMOCRATIC = 'Democratic'
REPUBLICAN = 'Republican'

TITLE_PATTERNS = {
    PRESIDENTIAL: re.compile(r'(\S+)\s\((D|R)(\S+)?\)'),
    VICE_PRESIDENTIAL: re.compile(r'(\S+)\s\((D|R)(\S+)?\)'),
    DEMOCRATIC: re.compile(r'(\w+)((\s\([\w\s]+\))|;)'),
    REPUBLICAN: re.compile(r'(\w+)((\s\([\w\s]+\))|;)'),
}

DEBATORS_BY_YEAR = {
    2012: {
        PRESIDENTIAL: {
            'OBAMA': 'D',
            'ROMNEY': 'R',
        },
        VICE_PRESIDENTIAL: {
            'BIDEN': 'D',
            'RYAN': 'R',
        },
    },
    2008: {
        PRESIDENTIAL: {
            'OBAMA': 'D',
            'MCCAIN': 'R',
        },
        VICE_PRESIDENTIAL: {
            'BIDEN': 'D',
            'PALIN': 'R',
        },
    },
    2004: {
        PRESIDENTIAL: {
            'KERRY': 'D',
            'BUSH': 'R',
        }
        VICE_PRESIDENTIAL: {
            'EDWARDS': 'D',
            'CHENEY': 'R',
        },
        DEMOCRATIC: ['CLARK', 'LIEBERMAN', 'KUCINICH', 'DEAN', 'KERRY',
                     'SHARPTON', 'EDWARDS'],
    },
    2000: {
        PRESIDENTIAL: {
            'GORE': 'D',
            'BUSH': 'R',
        },
        VICE_PRESIDENTIAL: {
            'LIEBERMAN': 'D',
            'CHENEY': 'R',
        },
    },
    1996: {
        PRESIDENTIAL: {
            'CLINTON': 'D',
            'DOLE': 'R',
        },
        VICE_PRESIDENTIAL: {
            'GORE': 'D',
            'KEMP': 'R',
        },
    },
    1992: {
        PRESIDENTIAL: {
            'CLINTON': 'D',
            'BUSH': 'R',
        },
        VICE_PRESIDENTIAL: {
            'GORE': 'D',
            'QUAYLE': 'R',
        },
    },
    1988: {
        PRESIDENTIAL: {
            'DUKAKIS': 'D',
            'BUSH': 'R',
        },
        VICE_PRESIDENTIAL: {
            'BENTSEN': 'D',
            'QUAYLE': 'R',
        },
    },
    1984: {
        PRESIDENTIAL: {
            'MONDALE': 'D',
            'REAGAN': 'R',
        },
        VICE_PRESIDENTIAL: {
            'FERRARO': 'D',
            'BUSH': 'R',
        },
    },
    1980: {
        PRESIDENTIAL: {
            'CARTER': 'D',
            'REAGAN': 'R',
        },
        VICE_PRESIDENTIAL: {
            'LIEBERMAN': 'D',
            'CHENEY': 'R',
        },
    },
    1976: {
        PRESIDENTIAL: {
            'CARTER': 'D',
            'FORD': 'R',
        },
        VICE_PRESIDENTIAL: {
            'MONDALE': 'D',
            'DOLE': 'R',
        },
    },
    1960: {
        PRESIDENTIAL: {
            'KENNEDY': 'D',
            'NIXON': 'R',
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

def init_transcript(soup, url):
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
