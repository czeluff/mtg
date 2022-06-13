from urllib.request import Request, urlopen
from functools import reduce
import pandas as pd
import bs4


# Given a format, return a DataFrame containing the card names
def mtgdecks_staples_frame(mtg_format):
    df = pd.DataFrame()
    df.name = mtg_format
    
    url = f'https://mtgdecks.net/{mtg_format}/staples'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=hdr)
    page = urlopen(req)

    soup = bs4.BeautifulSoup(page, features='html.parser')
    card_list_div = [div for div in soup.find(id='loadMoreCardsRow') if isinstance(div, bs4.element.Tag)] 

    df['Name'] = [card_div.find('b').text for card_div in card_list_div]
    df[f'{mtg_format}'] = [df.size] - df.index
    return df


def run():
    formats = [
        'Vintage',
        'Legacy',
        'Modern',
        'Pioneer',
        'Commander',
        'Premodern',
        'Pauper'
    ]

    # TODO: Add 'Cube' to formats, parse out of comparison of simpleman and wtwlf123

    # Create DataFrames per format
    dfs = [mtgdecks_staples_frame(mtg_format) for mtg_format in formats]

    # Merge all DataFrames into one
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['Name'], how='outer'), dfs)

    # Adding columns, without mucking the count
    df_total = df_merged.sum(axis=1, numeric_only=True)
    df_merged['Count'] = df_merged.count(axis=1, numeric_only=True)
    df_merged['Total'] = df_total

    # Add pricing information
    # TODO: add min price
    print(df_merged['Name'].tolist())

    # Export to CSV
    df_merged.sort_values(by=['Count', 'Name'], ascending=[False, True]).to_csv('mtg.csv')
