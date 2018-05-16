import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

MF_DICT_FNAME = 'data/raw/mf_dict.txt'

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


# construct_corpus constructs a corpus consisting of words from the Democratic
# and Republican candidates in a body of text.
def construct_corpus(text):
    lines = filter(None, text.split('\n')[1:])
    divider = lines.index('%')
    header, body = lines[:divider], lines[divider+1:]
    dems, reps = [], []
    for line in header:
        line = line.split('\t')
        if line[1] == 'R':
            reps.append(line[0])
        elif line[1] == 'D':
            dems.append(line[0])

    dem_corpus = ""
    rep_corpus = ""
    for line in body:
        is_dem = any([x in line for x in dems])
        is_rep = any([x in line for x in reps])
        line = line[line.find(':')+1:].strip()
        if is_dem:
            dem_corpus += line
        elif is_rep:
            rep_corpus += line
    dem_corpus = dem_corpus.decode('utf-8')
    rep_corpus = rep_corpus.decode('utf-8')

    return find_instances(dem_corpus), find_instances(rep_corpus)


# to_excel converts a corpus of Democratic and Republican words into an Excel
# spreadsheet formatted for perspective analysis.
def to_excel(dem_words, rep_words):
    writer = pd.ExcelWriter('data/excel/output.xlsx', engine='xlsxwriter')
    pd.DataFrame(
        spread_words(dem_words),
        columns=['word', 'foundations', 'instance', 'score']
    ).set_index('word').to_excel(writer, 'Democrats')
    pd.DataFrame(
        spread_words(rep_words),
        columns=['word', 'foundations', 'instance', 'score']
    ).set_index('word').to_excel(writer, 'Republicans')

    workbook = writer.book
    text_format = workbook.add_format({'text_wrap': True})
    for sheet in writer.sheets.values():
        sheet.set_column('B:B', 12.5, text_format)
        sheet.set_column('C:C', 67, text_format)

    writer.save()


# find_instances finds all instances of each MFD word in a corpus.
def find_instances(corpus):
    words = []
    lo_corp = corpus.lower()
    corp_len = len(corpus)
    for w in WORDS:
        if ' ' + w['word'].strip('*') in lo_corp:
            instances = w['pattern'].findall(corpus)
            if len(instances) > 0:
                words.append({
                    'word': w['word'],
                    'instances': instances,
                    'foundations': w['foundations'],
                    'frequency': len(instances) * 1.0 / len(corpus)
                })
    return words


# find_sig_diffs finds the words in a corpus's two word lists that significantly
# differ in frequency.
def find_sig_diffs(dem_words, rep_words):
    dem_stems = {x['word']: x for x in dem_words}
    rep_stems = {x['word']: x for x in rep_words}
    diffs = []
    for w in WORDS:
        stem = w['word']
        if stem in dem_stems and stem in rep_stems:
            diffs.append(dem_stems[stem]['frequency'] - rep_stems[stem]['frequency'])
        elif stem in dem_stems:
            diffs.append(dem_stems[stem]['frequency'])
        elif stem in rep_stems:
            diffs.append(rep_stems[stem]['frequency'])
    xbar = np.mean(diffs)
    s = np.std(diffs)
    z_scores = [(x-xbar)*1.0 / s for x in diffs]
    _, _, _ = plt.hist(z_scores)
    plt.show()


# spread_words reduces a word list into  a pandas-compatible data structure
# with one instance of each word as its own row.
def spread_words(words):
    data = []
    for w in words:
        for instance in w['instances']:
            data.append({
                'word': w['word'],
                'instance': instance,
                'foundations': ', '.join(
                    [FOUNDATIONS[f] for f in w['foundations']]
                ),
            })
    return data


if __name__ == '__main__':
    init_mf_dict()
    """
    fname = 'data/raw/Presidential-2012-10-16.txt'
    with open(fname) as f:
        s = f.read()
        dem_words, rep_words = construct_corpus(s)
        w = open('cac.he', 'w')
        w.write(str(dem_words))
        w.write('%')
        w.write(str(rep_words))
    """
    with open('cac.he') as f:
        [dem_words, rep_words] = [eval(x) for x in f.read().split('%')]
        find_sig_diffs(dem_words, rep_words)
