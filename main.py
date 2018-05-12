import re

MF_DICT_FNAME = 'data/mf_dict.txt'

# FOUNDATIONS serves as a hash map for 10 moral cores (virtue and vice for each
# moral foundation). The moral foundations dictionary starts its indexing at 1.
FOUNDATIONS = ['']

WORDS = []

# load_mf_dict loads the moral foundations dictionary. It is available at:
# http://www.moralfoundations.org/sites/default/files/files/downloads/moral%20foundations%20dictionary.dic
def init_mf_dict():
    with open(MF_DICT_FNAME) as mf:
        lines = filter(None, mf.read().split('\n')[1:])
        divider = lines.index('%')
        header, words = lines[:divider], lines[divider+1:]
        for line in header:
            FOUNDATIONS.append(line.split('\t')[1])
        for line in words:
            line = line.split('\t')
            word = line[0]
            WORDS.append({
                'word': word,
                'foundations': [int(x) for x in line[1].split(' ')],
                'pattern': get_pattern(word),
                'instances': []
            })


# get_pattern returns a regular expression for a word stem to capture the
# sentences surrounding each word.
def get_pattern(word):
    if '*' in word:
        word = word.replace('*', '\w*')
    return re.compile(
        '[^.?!]*[.?!][^.?!]*(?<=[.?\s!])' +
        word +
        '(?=[\s.?!])[^.?!]*[.?!][^.?!]*[.?!]'
    )


def analyze_corpus(corpus):
    lines = filter(None, corpus.split('\n')[1:])
    divider = lines.index('%')
    header, body = lines[:divider], lines[divider+1:]
    democrats, republicans = [], []
    for line in header:
        line = line.split('\t')
        if line[1] == 'R':
            republicans.append(line[0])
        elif line[1] == 'D':
            democrats.append(line[0])

    democratic_corpus = ""
    republican_corpus = ""
    for line in body:
        is_democratic = any([x in line for x in democrats])
        is_republican = any([x in line for x in republicans])
        line = line[line.find(':')+1:].strip()
        if is_democratic:
            democratic_corpus += line
        elif is_republican:
            republican_corpus += line

    democratic_words = find_instances(democratic_corpus)
    republican_words = find_instances(republican_corpus)
    for w in republican_words:
        if len(w['instances']) == 0:
            continue
        print "== %s =====" % w['word']
        for i in w['instances']:
            print "- " + i

def find_instances(corpus):
    words = WORDS[:]
    lo_corp = corpus.lower()
    for w in words:
        if ' ' + w['word'].strip('*') in lo_corp:
            w['instances'] = w['pattern'].findall(corpus)
            print w['word'], len(w['instances'])
    return words


if __name__ == '__main__':
    init_mf_dict()
    fname = 'data/Presidential-2012-10-03.txt'
    with open(fname) as f:
        s = f.read()
        analyze_corpus(s)
