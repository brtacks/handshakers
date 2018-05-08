from bs4 import BeautifulSoup as bs4
from datetime import date

import requests
import re

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
            try:
                year = int(year_label.text)
            except ValueError:
                pass
        if tr.a and year <= 2000:
            url = tr.a.attrs['href']
            create_transcript(url, year)


# create_transcript creates a transcript dictionary.
def create_transcript(url, year):
    soup = get_soup(url)
    transcript = init_transcript(soup, url)
    transcript['debaters'] = get_debater_lines(
        soup,
        transcript['debate_type'],
        year, # Year of election
        transcript['date'], # Date of debate
    )
    if len(transcript['debaters']) == 0:
        raise ValueError("No participants found: %s" % url)
    for v in transcript['debaters'].values():
        if len(v['lines']) == 0:
            raise ValueError("Debater %s has zero lines: %s" % (v, url))
    print_transcript(transcript)


# get_debater_lines finds each candidate and every line they spoke.
# It takes a soup, the debate_type, the year of the election, and the date of
# the debate.
def get_debater_lines(soup, debate_type, year, datetime):
    transcript = soup.find('span', attrs={'class': 'displaytext'})
    debaters = find_debaters(transcript, debate_type, year, datetime)
    lines = transcript.find_all('p')
    debater_lines = {}
    debaters.pop('pattern', None)
    if len(debaters) == 0:
        return debaters

    current_debater = None
    for line in lines:
        text = line.text
        speaker_match = line_speaker(line, debate_type, year)
        if speaker_match:
            speaker = speaker_match.group(1).upper()
            if speaker == 'PRESIDENT':
                speaker = PRESIDENTS_BY_YEAR[year]
            if speaker in debaters:
                current_debater = speaker
                text = text[
                    text.find(speaker_match.group()) +
                    len(speaker_match.group()):
                ]
            else:
                current_debater = None
        if current_debater:
            debaters[current_debater]['lines'].append(text.strip())

    return debaters


# The format of debate transcript varies by year and debate type (presidential
# or primary).
def find_debaters(soup, debate_type, year, datetime):
    debaters = None

    # In some special cases, participants are not listed at the beginning of the
    # transcript nor clearly introduced during the debate. In these cases, it is
    # simpler and more efficient to hardcode the participants.
    if datetime == date(2007, 6, 3):
        debaters = [['DODD', 'EDWARDS', 'CLINTON', 'OBAMA', 'RICHARDSON',
                     'BIDEN', 'KUCINICH'], 'D']
    elif datetime == date(1999, 12, 6):
        debaters = [['BAUER', 'BUSH', 'HATCH', 'MCCAIN', 'KEYES', 'FORBES'],
                    'R']
    elif datetime == date(1999, 10, 22):
        debaters = [['BAUER', 'HATCH', 'MCCAIN', 'KEYES', 'FORBES'], 'R']
    if debaters is not None:
        return {
            x: {
                'lines': [],
                'party': debaters[1]
            } for x in debaters[0]
        }
    try:
        debaters = DEBATERS_BY_YEAR[year][debate_type]
        if type(debaters) is dict:
            debaters = debaters.copy()
            for k, v in debaters.items():
                debaters[k] = {
                    'lines': [],
                    'party': v,
                }
            return debaters
        elif type(debaters) is list:
            return {
                x: {
                    'lines': [],
                    'party': 'D',
                } for x in debaters
            }
    except KeyError:
        # Debaters aren't hardcoded into the dictionary because the scraped
        # website listed the participants at the beginning of the transcript.
        pass

    pattern = TITLE_PATTERNS[TITLE_P]
    debaters = {}
    for idx, i in enumerate(soup.children):
        if i.name == 'p':
            # The participants list is in non-p tags at the top of the
            # transcript.
            # However, the list may also be stored under the header "Candidates"
            # because of a few pranksters at UC Santa Barbara.
            if idx == 1 and i.b and "Candidates" in i.b.text:
                matches = re.finditer(
                    r'(\w+)(?:\sJr\.)?(?:,\s([-\w\s\.]+)|;)',
                    str(i)
                )
            elif idx == 0:
                # The list may also be stuck between two <p>'s due to bad
                # employees at UC Santa Barbara, and we need to check.
                matches = re.finditer(r'(\w+)(?:\s\(([\w\s-]+)\)|;)', str(i))
            else:
                break
            for m in matches:
                if 'and' in m.group():
                    continue
                name = m.group(1)
                if PRESIDENTIAL in debate_type:
                    party = m.group(2)[0]
                else:
                    party = debate_type[0]
                debaters[name.upper()] = {
                    'lines': [],
                    'party': party
                }
            if len(debaters) > 0:
                return debaters
        match = re.search(r'(\w+)(?:,\sJr\.)?(?:\s\(([-\w\s\.,]+)\)|;)', str(i))
        name, party = None, None
        if match:
            name = match.group(1)
            if PRESIDENTIAL in debate_type:
                party = match.group(2)[0]
            else:
                party = debate_type[0]
        elif i.name is None:
            if i.strip() == '':
                continue
            name = i.split(' ')[-1].upper()
            for year in DEBATERS_BY_YEAR.values():
                for debate in year.values():
                    if name in debate:
                        party = debate[name]
            if party is None:
                print "Could not find party for title " +  str(i)
        if name is not None and party is not None:
            debaters[name.upper()] = {
                'lines': [],
                'party': party
            }
    return debaters


# line_speaker finds the speaker's name in a string as a regex match object.
def line_speaker(line, debate_type, year):
    try:
        title = DEBATERS_BY_YEAR[year][debate_type]
        if type(title) is list:
            # If debaters are stored in a list instead of in a dictionary,
            # they belong in the same party and need no party value.
            title = TITLE_A
        else:
            title = title['pattern']
    except KeyError:
        title = TITLE_P
    pattern = TITLE_PATTERNS[title]
    match = None

    ignored_titles = re.compile(r'(?i)(?:The|Mr|Ms|Mrs|Gov|Sen|Rep)\.')

    if title == TITLE_A or title == TITLE_P:
        # Speaker titles are in bold and match '(?i)(\w+):'
        if line.b:
            text = ignored_titles.sub('', line.b.text)
            match = re.search(r'(?i)(\w+):', text)
            if match is None:
                match = re.search(r'<b>([\w]+)<\/b>:', str(line))
                if match is None:
                    match = re.search(r'<b>([\w]+)<\/b><b>:', str(line))
            else:
                if match.group(1) == 'CANDIDATE':
                    match = re.search(
                        r'(\w+)(?:,\sJr\.)?(?:\s\([-\w\s\.,]+\))',
                        text
                    )
        else:
            if match is None:
                title = TITLE_C
    if title == TITLE_B:
        # Speaker titles are in italics and match '(?i)(\w+)\.'
        if line.i:
            text = ignored_titles.sub('', line.i.text)
            match = re.search(pattern, text)
    if title == TITLE_C:
        # Speaker titles are at the beginning of the line.
        text = ignored_titles.sub('', line.text).strip()
        if ':' in line:
            # Case 1 titles match '([A-Z]+):'
            match = re.search(r'([A-Z]+):', text)
        else:
            # Case 2 titles match '(?i)^([\w{2,}]+)(?:\.|:)'
            match = re.search(r'(?i)^([\w]{2,})(?:\.|:)', text)

    return match


def init_transcript(soup, url):
    date = soup.find('span', attrs={'class': 'docdate'})
    date = get_date_from_str(date.text)
    papers_title = soup.find('span', attrs={'class': 'paperstitle'}).text
    debate_type = None
    if 'Vice' in papers_title:
        debate_type = VICE_PRESIDENTIAL
    elif 'Democratic' in papers_title:
        debate_type = DEMOCRATIC
    elif 'Republican' in papers_title or 'Forum' in papers_title:
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
        print "  %s (%s): %d lines spoken" % (name, v['party'], len(v['lines']))
    print

if __name__ == '__main__':
    collect_transcripts()
#    url = 'http://www.presidency.ucsb.edu/ws/index.php?pid=74349'
#    create_transcript(url, 2008)
