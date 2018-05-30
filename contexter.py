from scipy.stats import norm

import re
import os
import math
import pandas as pd
import numpy as np

MF_DICT_FNAME = 'data/raw/mf_dict.txt'

FOUNDATIONS = []

WORDS = []

# load_mf_dict loads the moral foundations dictionary. It can be found at
# https://github.com/brass-tacks/the-other-side.
def init_mf_dict():
    foundations = []
    words = []
    with open(MF_DICT_FNAME) as mf:
        lines = filter(None, mf.read().split('\n')[1:])
        divider = lines.index('%')
        header, keywords = lines[:divider], lines[divider+1:]
        for line in header:
            foundations.append(line.split('\t')[1])
        for line in keywords:
            line = line.split('\t')
            word = line[0]
            words.append({
                'word': word,
                'foundations': [int(x) for x in line[1].split(' ')],
                'pattern': get_pattern(word),
                'instances': []
            })
    return foundations, words


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


# generate_context converts a debate transcript into an Excel spreadsheet for
# qualitative context scoring.
def generate_contexts():
    writer = pd.ExcelWriter('data/writer.xlsx', engine='xlsxwriter')

    files = sorted(
        [f for f in os.listdir('data/raw/') if f.find('Presidential') == 0]
    )
    for fname in files:
        if fname.find('Presidential') != 0:
            continue
        with open('data/raw/' + fname) as f:
            s = f.read()
            print "== Generating context for %s =====" % fname
            dem_words, rep_words = construct_corpus(s)
            print "  - Corpus constructed."
            dem_instances, rep_instances = find_sig_diffs(dem_words, rep_words)
            print "  - Diffs generated."
            write_to_excel(
                fname[fname.find('-') + 1:fname.rfind('.')],
                dem_instances,
                rep_instances,
                writer,
            )
        print "  > Done.\n"

    workbook = writer.book
    text_format = workbook.add_format({'text_wrap': True})
    for sheet in writer.sheets.values():
        sheet.set_column('B:B', 12.5, text_format)
        sheet.set_column('C:C', 67, text_format)

    writer.save()

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


# write_to_excel converts a corpus of Democratic and Republican words into an
# Excel spreadsheet formatted for perspective analysis.
def write_to_excel(fname, dem_words, rep_words, writer):
    pd.DataFrame(
        spread_words(dem_words),
        columns=['word', 'foundations', 'instance', 'score']
    ).set_index('word').to_excel(writer, fname + ' (D)')
    pd.DataFrame(
        spread_words(rep_words),
        columns=['word', 'foundations', 'instance', 'score']
    ).set_index('word').to_excel(writer, fname + ' (R)')


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
    diffs = {}
    for w in WORDS:
        stem = w['word']
        d = None
        if stem in dem_stems and stem in rep_stems:
            d = math.fabs(
                dem_stems[stem]['frequency'] - rep_stems[stem]['frequency']
            )
        elif stem in dem_stems:
            d = dem_stems[stem]['frequency']
        elif stem in rep_stems:
            d = rep_stems[stem]['frequency']
        else:
            continue
        diffs[stem] = d
    diff_values = diffs.values()
    xbar = np.mean(diff_values)
    s = np.std(diff_values)

    # Converting all diffs to z-scores
    z_scores = {
        stem: (diffs[stem]-xbar) / s
        for stem in diffs
    }

    # Converting all z-scores to p-values, but we only want differences that are
    # significantly large rather than small.
    p_values_ary = [
        (stem, 1.0 - norm.cdf(z_scores[stem]))
        for stem in z_scores if z_scores[stem] > 0
    ]
    sig_stems = [stem for stem, p in p_values_ary if p < 0.1]

    dem_instances = []
    rep_instances = []
    for w in WORDS:
        word = w['word']
        if word in sig_stems:
            if word in dem_stems:
                dem_instances.append(dem_stems[word])
            if word in rep_stems:
                rep_instances.append(rep_stems[word])

    return dem_instances, rep_instances


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
    FOUNDATIONS, WORDS = init_mf_dict()
    # FOUNDATIONS serves as a hash map for 10 moral cores (virtue and vice for
    # each moral foundation). The moral foundations dictionary starts its
    # indexing at 1.
    FOUNDATIONS = [''] + FOUNDATIONS

    generate_contexts()
