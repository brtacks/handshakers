import pandas as pd
import numpy as np
import copy
import math
import pickle
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
        debates = [
            d for d in all_debates if str(year) in d
        ]
        if len(debates) == 0:
            continue

        # We now have foundation scores for both Dem's and Rep's.
        dem_founds, rep_founds = reduce_campaign( xl, debates )
        plot_foundations( dem_founds, rep_founds, year )


def plot_foundations(dem_founds, rep_founds, year):
    # Plotting the bars
    fig, ax = plt.subplots( figsize=(10,5) )

    foundations, _ = contexter.init_mf_dict()

    chart_data = {
        # Remove '__Virtue' and '__Vice' from the foundation names
        'foundations': [ f[ :-len('Virtue') ] for f in foundations
                         if 'Virtue' in f ],

        # For each moral foundation, subtract its Vice score from its Virtue
        # score
        'dem': [ dem_founds[ foundations[f] ] -
                 dem_founds[ foundations[f+1] ]
                 for f in range( 0, len(foundations), 2 )],
        'rep': [ rep_founds[ foundations[f] ] -
                 rep_founds[ foundations[f+1] ]
                 for f in range( 0, len(foundations), 2 )],
    }
    chart_df = pd.DataFrame(
        chart_data,
        columns=[ 'foundations', 'dem', 'rep' ],
    )

    iota = np.arange(len(foundations) / 2) # Why didn't I do this in Go
    width = 0.3 # width of the bars

    # Create the Democrat bar
    plt.bar(
        iota,
        chart_df['dem'],
        width,
        color='b',
        label=chart_df['foundations'][0]
    )
    # Create the Republican bar
    plt.bar(
        iota + width,
        chart_df['rep'],
        width,
        color='r',
        label=chart_df['foundations'][0]
    )

    ax.set_xticks( iota + 0.5*width )
    ax.set_xticklabels( chart_df['foundations'] )
    ax.set_title( str(year) )

    plt.legend(['dem', 'rep'], loc='upper right')
    plt.show()


# reduce_campaign reduces a year's debates into values for each moral foundation
# for each party. It takes the contexter and  a list of sheet names,
def reduce_campaign(contexter, debates):
    dem_foundations = copy.deepcopy( FOUNDATIONS )
    rep_foundations = copy.deepcopy( FOUNDATIONS )

    for sheet_name in debates:
        if '(D)' in sheet_name:
            reduce_debate( contexter.parse(sheet_name), dem_foundations )
        elif '(R)' in sheet_name:
            reduce_debate( contexter.parse(sheet_name), rep_foundations )

    for f, scores in dem_foundations.items():
        if len(scores) == 0:
            dem_foundations[f] = 0
        else:
            dem_foundations[f] = sum(scores) * 1.0 / len(scores)
    for f, scores in rep_foundations.items():
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
            print('Foundation {} does not exist.'.format(f))
            sys.exit(1)
        if ',' in f:
            print('Foundations {} need to be narrowed down.'.format(f))
        if math.isnan(score):
            print('No score given in: ' + row['instance'])
            sys.exit(1)
        foundations[f].append(score)


if __name__ == '__main__':
    foundations, _ = contexter.init_mf_dict()
    FOUNDATIONS = { f: [] for f in foundations }
    scan_contexter()


