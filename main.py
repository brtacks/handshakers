from bs4 import BeautifulSoup
import requests
import shutil


WIKI_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
DEBATES_LIST_URL = 'https://en.wikipedia.org/wiki/United_States_presidential_' \
                   'debates#1960_Kennedy%E2%80%93Nixon_debates'


# The graphic we are creating only requires one face for each party for each
# year. Moreover, we are not considering independents. PRESIDENTIAL_CANDIDATES
# ignores independents like Ross Perot and "third wheels" like John B. Anderson.
CANDIDATES = [
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


# get_face_urls gets the image urls for the faces of every candidate.
def get_face_urls():
    urls = []

    for title in CANDIDATES:
        r = requests.get(
            WIKI_ENDPOINT,
            params={
                'action': 'query',
                'prop': 'pageimages',
                'format': 'json',
                'pithumbsize': 200,
                'titles': title,
            }
        )

        pages = r.json()['query']['pages']
        if len(pages) == 0:
            print('No wikipedia page found for {}. Skipping candidate.'
                  .format(r.url))
            continue
        if len(pages) > 1:
            print('Multiple wikipedia pages found for {}. Skipping candidate.'
                  .format(r.url))
            continue

        try:
            urls.append( list(pages.values())[0]['thumbnail']['source'] )
        except (KeyError, IndexError) as e:
            print('Unexpected JSON format for {}.\nIn pages: {}'
                  .format(r.url, pages))

    return urls


if __name__ == '__main__':
    face_urls = get_face_urls()
    print(face_urls)
