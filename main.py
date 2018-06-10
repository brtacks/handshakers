import pandas as pd
import numpy as np
import copy
import math
import sys
import contexter

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

CONTEXTER_FNAME = 'data/contexter.xlsx'

FOUNDATIONS = {}


import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '--graph',
    help='option to display certain types of plots'
)

args = parser.parse_args()


# scan_contexter reduces our qualitative analysis on a year-by-year basis.
def scan_contexter():
    xl = pd.ExcelFile( CONTEXTER_FNAME )

    all_debates = xl.sheet_names

    all_campaigns = []

    for year in range(1960, 2017, 4):
        debates = [
            d for d in all_debates if str(year) in d
        ]
        if len(debates) == 0:
            continue

        # We now have foundation scores for both Dem's and Rep's.
        dem_founds, rep_founds = reduce_campaign( xl, debates )
        print( 'Reduced the {} debate.'.format(year) )

        all_campaigns.append({
            'D': dem_founds,
            'R': rep_founds,
            'year': year,
        })

    if args.graph == 'bar':
        plot_all_bar_foundations(all_campaigns)
    elif args.graph == 'line':
        plot_all_line_foundations(all_campaigns)


# plot_all_bar_foundations calls plot_bar_foundations for each year.
def plot_all_bar_foundations(all_campaigns):
     for campaign in all_campaigns:
         plot_bar_foundations(
             campaign['D'],
             campaign['R'],
             campaign['year']
         )


# plot_bar_foundations plots the foundation scores in a double bar chart for one
# year.
def plot_bar_foundations(dem_founds, rep_founds, year):
    print(
        'Plotting bar {} foundation scores...'.format(year),
        end='',
        flush=True
    )

    # Plotting the bars
    fig, ax = plt.subplots( figsize=(10,8) )

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

    print('[DONE]')


# plot_all_line_foundations calls plot_line_foundations for each foundation.
def plot_all_line_foundations(all_campaigns):

    # For each foundation, plot its lines.
    for f in [ f[ :-len('Virtue') ] for f in foundations if 'Virtue' in f ]:
        plot_foundation_lines(all_campaigns, f)


# plot_foundation_lines plots the foundation scores of each foundation in a
# dobule line chart.
def plot_foundation_lines(all_campaigns, foundation):
    print(
        'Plotting foundation lines for {}...'.format( foundation ),
        end='',
        flush=True
    )

    chart_data = {
        'dem': [],
        'rep': [],
        'year': [],
    }

    for campaign in all_campaigns:
        chart_data['dem'].append(
            campaign['D'][ foundation + 'Virtue'] -
            campaign['D'][ foundation + 'Vice' ]
        )
        chart_data['rep'].append(
            campaign['R'][ foundation + 'Virtue'] -
            campaign['R'][ foundation + 'Vice' ]
        )
        chart_data['year'].append( campaign['year'] )

    chart_df = pd.DataFrame(chart_data)

    dem, = plt.plot( 'year', 'dem', data=chart_df, color='b' )
    rep, = plt.plot( 'year', 'rep', data=chart_df, color='r' )

    plt.title( foundation )
    plt.xlabel( 'year')
    plt.ylabel( 'score' )
    plt.legend()

    fig = plt.gcf()
    fig.set_size_inches(10, 8, forward=True)
    plt.show()

    print('[DONE]')


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
            dem_foundations[f] = sum(scores) # * 1.0 / len(scores)
    for f, scores in rep_foundations.items():
        if len(scores) == 0:
            rep_foundations[f] = 0
        else:
            rep_foundations[f] = sum(scores) # * 1.0 / len(scores)

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


