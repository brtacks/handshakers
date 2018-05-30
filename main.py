import pandas as pd
import numpy as np
import math
import sys
import contexter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

CONTEXTER_FNAME = 'data/contexter.xlsx'

FOUNDATIONS = {}


# scan_contexter reduces our qualitative analysis on a year-by-year basis.
def scan_contexter():
    xl = pd.ExcelFile( CONTEXTER_FNAME )

    all_debates = xl.sheet_names

    for year in range(1960, 2017, 4):
        print '%d:' % year
        debates = [
            d for d in all_debates if str(year) in d
        ]
        # We now have foundation scores for both Dem's and Rep's.
        dem_founds, rep_founds = reduce_campaign( xl, debates )

        # We have to make sure the bars are in order. The scores of each
        # foundation's virtue are subtracted by each the scores of each
        # foundation's vice.
        iterf = iter( FOUNDATIONS ) # To iterate over two values at a time
        data = [
            [
                rep_founds[f] - rep_founds[ next(iterf) ]
                for f in iterf
            ],
        ]

        X = np.arange( len(FOUNDATIONS) / 2 )
        plt.bar(
            X + 0.00,
            [ dem_founds[f] - dem_founds[ next(iterf) ] for f in iterf ],
            color='b',
            width=0.3,
        )
        plt.bar(
            X + 0.25,
            [ rep_founds[f] - rep_founds[ next(iterf) ] for f in iterf ],
            color='r',
            width=0.3,
        )
        plt.show()

        break


# reduce_campaign reduces a year's debates into values for each moral foundation
# for each party. It takes the contexter and  a list of sheet names,
def reduce_campaign(contexter, debates):
    dem_foundations = FOUNDATIONS.copy()
    rep_foundations = FOUNDATIONS.copy()

    for sheet_name in debates:
        if '(D)' in sheet_name:
            reduce_debate( contexter.parse(sheet_name), dem_foundations )
        elif '(R)' in sheet_name:
            reduce_debate( contexter.parse(sheet_name), rep_foundations )

    for f, scores in dem_foundations.iteritems():
        if len(scores) == 0:
            dem_foundations[f] = 0
        else:
            dem_foundations[f] = sum(scores) * 1.0 / len(scores)
    for f, scores in rep_foundations.iteritems():
        if len(scores) == 0:
            rep_foundations[f] = 0
        else:
            rep_foundations[f] = sum(scores) * 1.0 / len(scores)

    return dem_foundations, rep_foundations



# reduce_debate reduces a debate into values for each moral foundation for one
# party. It takes one quantitative analysis of one candidate in one debate (a
# dataframe).
def reduce_debate(debate, foundations):
    for _, row in debate.iterrows():
        f, score = row['foundations'], row['score']
        if f not in foundations:
            print 'Foundation %s does not exist.' % f
            sys.exit(1)
        if ',' in f:
            print 'Foundations %f need to be narrowed down.' % f
        if math.isnan(score):
            print 'No score given in: ' + row['instance']
            sys.exit(1)
        foundations[f].append(score)


if __name__ == '__main__':
    foundations, _ = contexter.init_mf_dict()
    FOUNDATIONS = { f: [] for f in foundations }

    scan_contexter()


