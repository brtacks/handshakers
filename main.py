MF_DICT_FNAME = 'data/mf_dict.txt'

FOUNDATIONS = ['']


# Load moral foundations dictionary, found at:
# http://www.moralfoundations.org/sites/default/files/files/downloads/moral%20foundations%20dictionary.dic
def load_mf_dict():
    with open(MF_DICT_FNAME) as mf:
        s = mf.read()
        s = filter(None, [x.strip() for x in s])
        header = s[1:s.rfind('%')]
        for line in header:
            line = line.split(' ')
            foundations.append(line[-1])
        body = s[s.rfind('%') + 1:]
        # now we have to find the words

# regex for sentence b4 and after word match:
# [^.?!]*[.?!][^.?!]*(?<=[.?\s!])suffer[^\s\.\-]*(?=[\s.?!])[^.?!]*[.?!][^.?!]*[.?!]

# def analyze_corpus(corpus):


if __name__ == '__main__':
    load_mf_dict()
    fname = 'Presidential-2012-10-3.txt'
    with open(fname) as f:
        s = f.read()
        analyze_corpus(s)
