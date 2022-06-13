from urllib.request import Request, urlopen
from functools import reduce
import pandas as pd
import bs4
import json
import sys


# Given a format, return a DataFrame containing the card names
def mtgdecks_staples_frame(mtg_format, pages=1):
    df = pd.DataFrame()
    df.name = mtg_format
    
    url_base = f'https://mtgdecks.net/{mtg_format}/staples'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    card_list_div = []

    for pageNumber in range(0, pages):
        first_page = (pageNumber == 0)

        url = url_base if first_page else f'{url_base}/page:{pageNumber}'
        req = Request(url, headers=hdr)
        page = urlopen(req)

        soup = bs4.BeautifulSoup(page, features='html.parser')
        section = soup.find(id='loadMoreCardsRow') if first_page else soup
        [card_list_div.append(div) for div in section if div.name == 'div']

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
    # TODO: Use argparse to clean up argument passing
    pages = int(sys.argv[2]) if len(sys.argv) == 3 else 1
    dfs = [mtgdecks_staples_frame(mtg_format, pages=pages) for mtg_format in formats]

    # Merge all DataFrames into one
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['Name'], how='outer'), dfs)

    # Adding columns, without mucking the count
    df_total = df_merged.sum(axis=1, numeric_only=True)
    df_merged['Count'] = df_merged.count(axis=1, numeric_only=True)
    df_merged['Total'] = df_total

    # Add pricing information
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        f = open(filename)
        cards = json.load(f)
        card_names = df_merged['Name'].tolist()
        priced_cards = list(filter(lambda card: card['name'] in card_names, cards))  # TODO: fix double-sided cards
        df_priced_cards = pd.DataFrame(priced_cards)

        # Adjust columns, compute Price
        df_priced_cards.rename(columns={'name': 'Name', 'prices': 'Price'}, inplace=True)
        df_priced_cards = df_priced_cards[['Name', 'Price']]
        df_priced_cards['Price'] = df_priced_cards['Price'].apply(lambda x: x['usd']).astype(float)
        df_priced_cards = df_priced_cards.sort_values(['Name', 'Price']).drop_duplicates(subset=['Name'], keep='first')
        df_merged = pd.merge(df_merged, df_priced_cards, on='Name', how='left')

        # Construct a 'Value'
        # TODO: construct a better value
        value = (df_merged['Price'] / df_merged['Total'])
        df_merged['Value'] = value
        # max_value = value.max()
        # df_merged['Value'] = [1] - ((value / [max_value]) / df_merged['Count'])

    # Export to CSV
    # df_merged.sort_values(by=['Count', 'Value'], ascending=[False, True]).to_csv('mtg.csv')
    df_merged.sort_values(by=['Count'], ascending=[False]).to_csv('mtg.csv')