import pandas as pd
import contexter

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
        reduce_campaign( xl, debates )
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


# reduce_debate reduces a debate into values for each moral foundation for one
# party. It takes one quantitative analysis of one candidate in one debate (a
# dataframe).
def reduce_debate(debate):
    pass

if __name__ == '__main__':
    foundations, _ = contexter.init_mf_dict()
    FOUNDATIONS = { f: 0 for f in foundations }

    scan_contexter()


