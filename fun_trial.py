# -*- coding: utf-8 -*-

from get_sreality_data import get_response, create_reality_list
import pandas as pd


# parameters to get data from sreality

api_url = "https://www.sreality.cz/api/cs/v2/estates"
params_1 = {
        # flat
        "category_main_cb": "1", 
        # size, 1kk, 2kk and 3kk
        "category_sub_cb": "2%7C4%7C6", 
        "category_type_cb": "1",        
        "locality_region_id": "10", #Prague
        "page": "1",
        "estate_age": "2"
        }   



def get_all_data(api_url, params):
    """To get data from sreality based on the given params """
     
    total_reality_list = []
    page = 1
    
    # to get the first response
    number_pages, data_reality = get_response(api_url, params, True)
    
    while page <= number_pages:
        reality_list = create_reality_list(data_reality)
        total_reality_list.extend(reality_list)
        page = page + 1
        params["page"] = str(page)
        data_reality = get_response(api_url, params, False)

    init_reality_df = pd.DataFrame(data = total_reality_list)
    init_reality_df["size"] = pd.to_numeric(init_reality_df["size"])

        
    return init_reality_df

reality_df = get_all_data(api_url, params_1)
reality_df.info()

#-----------------------------------------------------------------------------

# multiple select 1kk, 2kk, 3kk
disposition_list = ['1kk', '2kk', '3kk']
    
# df of characteristics
total_characteristics = {}
for disp in disposition_list:
    df = reality_df[reality_df.disposition == disp]
    characteristics = {}
    characteristics['Count total'] = df.id.count()
    
    characteristics['Count personal'] = df.personal.sum()
    
    characteristics['Count new flats'] = df.new.sum()
    
    characteristics['Average price, CZK'] = round(df.price.mean(), 0)
    characteristics['Maximum price, CZK'] = round(df.price.max(), 0)
    characteristics['Minimum price, CZK'] = round(df.price.min(), 0)
    
    characteristics['Average size, m2'] = round(df['size'].mean(), 2)
    characteristics['Maximum size, m2'] = round(df['size'].max(), 2)
    characteristics['Minimum size, m2'] = round(df['size'].min(), 2)
    
    total_characteristics[disp] = characteristics

characteristics_df = pd.DataFrame(total_characteristics)
char_cols = characteristics_df.columns
if len(char_cols) > 1:
    characteristics_df['All_flats'] = characteristics_df.sum(axis = 1)
    
    characteristics_df.loc['Average price, CZK', 'All_flats'] =  round(characteristics_df.loc[
        'Average price, CZK', char_cols].mean(), 0)
    characteristics_df.loc['Average size, m2', 'All_flats'] =  round(characteristics_df.loc[
        'Average size, m2', char_cols].mean(), 2)
    characteristics_df.loc['Maximum price, CZK', 'All_flats'] =  characteristics_df.loc[
        'Maximum price, CZK', char_cols].max()
    characteristics_df.loc['Maximum size, m2', 'All_flats'] =  characteristics_df.loc[
        'Maximum size, m2', char_cols].max()
    characteristics_df.loc['Minimum price, CZK', 'All_flats'] =  characteristics_df.loc[
        'Minimum price, CZK', char_cols].min()
    characteristics_df.loc['Minimum size, m2', 'All_flats'] =  characteristics_df.loc[
        'Minimum size, m2', char_cols].min()
    
    
char_to_show = characteristics_df.T
char_to_show.columns
char_to_show = char_to_show[['Count total', 'Count personal', 'Count new flats', 'Average price, CZK', 'Maximum price, CZK',
                                      'Minimum price, CZK', 'Average size, m2', 'Maximum size, m2', 'Minimum size, m2']]

# char_to_show = characteristics_df.T[['Count total', 'Count personal', 'Count new flats',
#                                      'Average price, CZK', 'Maximum price, CZK',
#                                      'Minimum price, CZK', 'Average size, m2',
#                                      'Maximun size, m2', 'Minimum size, m2' ]]
# to show dfs
# total df

reality_df['price_per_m2'] = reality_df['price']/reality_df['size']

price_district = reality_df.groupby(['district', 'disposition'])['price_per_m2'].mean()

colors_map = {'1kk': '#008B8B','2kk': '#8B008B', '3kk': '#483D8B'}

import plotly.graph_objects as go
from plotly.subplots import make_subplots


# graph of price distribution for each dispozition
fig = make_subplots(rows = 1, cols = len(disposition_list),
                    subplot_titles=[i + " Prices, CZK" for i in disposition_list])

for i in range(len(disposition_list)):
    cur_x = reality_df.loc[
        reality_df.disposition == disposition_list[i]].price
    fig.add_trace(go.Histogram(x = cur_x, 
                               marker_color = colors_map[disposition_list[i]]), 
        row = 1, col = i + 1)
    fig.add_vline(
    x=cur_x.mean(),
    line_color="Red", line_dash = "dash",
    layer="above", line_width=2,
    row = 1, col = i + 1
)


fig.update_layout(showlegend = False, 
                  height = 500)



# graph of size/price coloring by dispozition
fig_scatter = go.Figure(data = go.Scatter(
    x = reality_df['size'], y = reality_df.price,
    marker_color = reality_df.disposition.map(colors_map),
    mode = 'markers',
    text = reality_df.name,
    showlegend = False,
    opacity = 0.7
    ))

fig_scatter.update_layout( 
                  #title_text = "Prices of flats based on their size",
                  height = 500, yaxis = {"title":"Price, CZK"}, xaxis = {"title": "Size, m2"})



import plotly.io as pio


pio.renderers.default='browser'
import plotly.io as pio

# to show picture in spyder directly
#pio.renderers.default='svg'    

        

