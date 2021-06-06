from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import io


def download_prices_history():
    """Returns dictionary of pandas dfs of the newest available flat prices index from the Czech statistical office
     in the following structure:
            {'older_flats_df': old_df,
            'new_flats_df': new_df}
     """
    r = requests.get('https://www.czso.cz/csu/czso/indexy-realizovanych-cen-bytu-4-ctvrtleti-2020')
    soup = BeautifulSoup(r.content, 'html.parser')

    # to get the latest link
    last_link = 'https://www.czso.cz' + soup.select('div#archiv-wrapper a')[0]['href']

    n_r = requests.get(last_link)
    if r.status_code != 200:
        print(f'link could not be reached, error code is {r.status_code}')
        quit()
    n_soup = BeautifulSoup(n_r.content, 'html.parser')

    ref_xls = dict()
    links_table = n_soup.select('div.portlet-Attachments a')
    # to create re expression for file name
    expr = re.compile('[1-9].[1-9]. *index.*xls.*')
    for link in links_table:
        if expr.match(link['title'].lower()):
            ref_xls[link['title']] = link['href']
    expr_new = re.compile('.*nov.*bytů.*')
    expr_old = re.compile('.*star.*bytů.*')

    def read_link_todf(expression, skip_rows, n_cols, header):
        """To return dfs with data based on expression and excel reading criteria"""
        file_cur = requests.get(ref_xls[list(filter(expression.match, ref_xls.keys()))[0]]).content
        # to get pandas df and drop empty columns and rows
        cur_df = pd.read_excel(io.BytesIO(file_cur), engine='openpyxl', skiprows=skip_rows, header=header).dropna(
            axis=1, how='all')
        cur_df = cur_df.iloc[:, :n_cols + 1].set_index(cur_df.columns[0])
        return cur_df

    old_df = read_link_todf(expr_old, 7, 3, [0, 1])
    new_df = read_link_todf(expr_new, 3, 1, 0)

    return {'older flats': old_df,
            'new flats': new_df}
