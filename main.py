import re
import pandas as pd
import numpy as np

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

    return find_instances(dem_corpus.decode('utf-8')), find_instances(rep_corpus.decode('utf-8'))


def to_excel(dem_words, rep_words):
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
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
    align = workbook.add_format({'valign': 'bottom'})
    for sheet in writer.sheets.values():
        sheet.set_column('A:A', None, align)
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
                })
    return words


# spread_words creates a pandas-compatible data structure with each instance of
# each word as its own row.
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
    fname = 'data/Presidential-2012-10-16.txt'
    with open(fname) as f:
        s = f.read()
        dem_words, rep_words = analyze_corpus(s)
        to_excel(dem_words, rep_words)
