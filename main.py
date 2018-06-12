from bs4 import BeautifulSoup
import requests


WIKI_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
DEBATES_LIST_URL = 'https://en.wikipedia.org/wiki/United_States_presidential_' \
                   'debates#1960_Kennedy%E2%80%93Nixon_debates'


# The graphic we are creating only requires one face for each party for each
# year. Moreover, we are not considering independents. PRESIDENTIAL_CANDIDATES
# ignores independents like Ross Perot and "third wheels" like John B. Anderson.
PRESIDENTIAL_CANDIDATES = [
    'John F. Kennedy', 'Richard Nixon',
    'Gerald Ford', 'Jimmy Carter',
    'Ronald Reagan',
    'Walter Mondale',
    'George H. W. Bush', 'Michael Dukakis',
    'Bill Clinton',
    'Bob Dole',
    'George W. Bush', 'Al Gore',
    'John Kerry',
    'John McCain', 'Barack Obama',
    'Mitt Romney',
    'Hillary Clinton', 'Donald Trump',
]


# get_candidates gets the titles of every candidate's Wikipedia page.
def get_candidates():
    r = requests.get( DEBATES_LIST_URL )
    soup = BeautifulSoup( r.content, 'html.parser' )
    table = soup.find('table', attrs={'class': 'wikitable'})

    candidates = []
    for tr in table.find_all('tr')[1:]: # parse every <tr> except header
        td = tr.find_all('td')[1]
        anchors = td.find_all('a')

        for a in anchors:
            title = a.attrs.get('title', '')
            if title in PRESIDENTIAL_CANDIDATES and title not in candidates:
                candidates.append( title )

    return candidates


# get_face_urls gets the image urls for the faces of every candidate.
def get_face_urls():
    candidates = get_candidates()

if __name__ == '__main__':
    face_urls = get_face_urls()
