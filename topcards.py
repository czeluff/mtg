from urllib.request import Request, urlopen
import pandas as pd
import bs4
    
# Given a format, return a DataFrame containing the card names
def mtgdecks_staples_frame(format):
    df = pd.DataFrame()
    df.name = format
    
    url = f'https://mtgdecks.net/{format}/staples'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=hdr)
    page = urlopen(req)

    soup = bs4.BeautifulSoup(page, features='html.parser')
    card_list_div = [div for div in soup.find(id='loadMoreCardsRow') if isinstance(div, bs4.element.Tag)] 

    df['Name'] = [card_div.find('b').text for card_div in card_list_div]
    df[f'{format}'] = True
    return df
    
formats = [
    'Vintage',
    'Legacy',
    'Modern',
    'Pioneer',
    'Commander',
    'Premodern',
    'Pauper'
]

dfs = [mtgdecks_staples_frame(format) for format in formats]

# print(dfs[0].head())

# Merging
merged_df = pd.concat(dfs)
print(merged_df)

# counted_merged_df = merged_df.groupby(['Name']).size().reset_index().rename(columns={0:'Count'}).sort_values(by=['Count', 'Name'], ascending=[False, True])
# print(counted_merged_df)