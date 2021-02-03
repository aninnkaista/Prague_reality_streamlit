# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 21:33:17 2021

@author: annaa
"""
import streamlit as st
from get_sreality_data import get_response, create_reality_list
import pandas as pd


st.set_page_config(layout = "wide")

st.title("Basic overview of flats for sale in Prague")

st.write("Summary of information about 1kk, 2kk and 3kk flats sales prices from sreality.cz.")

expander = st.beta_expander("Sources and inspirations")
expander.markdown("""
* Server for realities search in the Czech republic [sreality.cz](https://www.sreality.cz/)
* Python packages and corresponding libraries such as pandas, requests, streamlit, plotly;
* Educational video on youtube by Data Professor [Build 12 Data Science Apps with Python and Streamlit - Full Course] (https://www.youtube.com/watch?v=JwSS70SZdyM&t=6368s)
"""
)

# parameters to get data from sreality

api_url = "https://www.sreality.cz/api/cs/v2/estates"
params_init = {
        # flat
        "category_main_cb": "1", 
        # size, 1kk, 2kk and 3kk
        "category_sub_cb": "2%7C4%7C6", 
        "category_type_cb": "1",        
        "locality_region_id": "10", #Prague
        "page": "1"
        }   

# Page layout
col_1 = st.sidebar

col_1.header("User options")

# selectbox for the days to search flats for
age_options = {"1 day": 2, 
               "7 days": 8,
               "30 days": 31,
               "no limit": None}
estate_age = col_1.selectbox("Select for how many days to show the ads:", 
                             list(age_options.keys()),
                             1)

# append params for estate age if necessary
if estate_age != "no limit":
    params_1 = params_init.copy()
    params_1["estate_age"] = str(age_options[estate_age])
else:
    params_1 = params_init.copy()
#-----------------------------------------------------------------------------

# to send requests one page at a time
@st.cache
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
    init_reality_df.insert(4, 'price_per_m2', init_reality_df['price']/init_reality_df['size'])
        
    return init_reality_df

init_reality_df = get_all_data(api_url, params_1)


#-----------------------------------------------------------------------------

# select if personal
personal_char = col_1.checkbox("If only personal ownership", False)
# select if new
new_char = col_1.checkbox("If only new flat", False)

# slider for price
min_value = 1000000
max_value = 50000000
price_range = col_1.slider("Price range", min_value, max_value, 
                        (min_value, max_value),
                        step = 500000, format = '%d')

# slider for size
min_value = 10
max_value = 300
size_range = col_1.slider("Size range, m2", min_value, max_value, (min_value, max_value),
                        step = 5, format = '%d')

# multiple select 1kk, 2kk, 3kk
disposition_options = ['1kk', '2kk', '3kk']
disposition_list = col_1.multiselect("Select relevant flat dispositions",
                                  disposition_options,
                                  disposition_options)


# to download csv with results


# to filter reality_df according to the given parameters
filt_reality_df = init_reality_df.loc[
    # price
    (init_reality_df.price >= price_range[0]) &
    (init_reality_df.price <= price_range[1]) &
    # size
    (init_reality_df['size'] >= size_range[0]) &
    (init_reality_df['size'] <= size_range[1]) &
    # disposition
    (init_reality_df.disposition.isin(disposition_list))    
    ]
# to filter if personal
if personal_char:
    again_filt_reality_df = filt_reality_df[filt_reality_df.personal]
else:
    again_filt_reality_df = filt_reality_df.copy()

# to filter if new
if new_char:
    reality_df = again_filt_reality_df[again_filt_reality_df.new]    
else:
    reality_df = again_filt_reality_df.copy()
    
# df of characteristics
total_characteristics = {}
for disp in disposition_list:
    df = reality_df[reality_df.disposition == disp]
    characteristics = {}
    characteristics['Count total'] = df.id.count()
    
    characteristics['Count personal'] = df.personal.sum()
    
    characteristics['Count new flats'] = df.new.sum()
    
    characteristics['Average price, czk'] = round(df.price.mean(), 0)
    characteristics['Maximum price, czk'] = round(df.price.max(), 0)
    characteristics['Minimum price, czk'] = round(df.price.min(), 0)
    
    characteristics['Average size, m2'] = round(df['size'].mean(), 2)
    characteristics['Maximum size, m2'] = round(df['size'].max(), 2)
    characteristics['Minimum size, m2'] = round(df['size'].min(), 2)
    
    total_characteristics[disp] = characteristics

characteristics_df = pd.DataFrame(total_characteristics)
char_cols = characteristics_df.columns
if len(char_cols) > 1:
    characteristics_df['All_flats'] = characteristics_df.sum(axis = 1)
    
    characteristics_df.loc['Average price, czk', 'All_flats'] =  round(characteristics_df.loc[
        'Average price, czk', char_cols].mean(), 0)
    characteristics_df.loc['Average size, m2', 'All_flats'] =  round(characteristics_df.loc[
        'Average size, m2', char_cols].mean(), 2)
    characteristics_df.loc['Maximum price, czk', 'All_flats'] =  characteristics_df.loc[
        'Maximum price, czk', char_cols].max()
    characteristics_df.loc['Maximum size, m2', 'All_flats'] =  characteristics_df.loc[
        'Maximum size, m2', char_cols].max()
    characteristics_df.loc['Minimum price, czk', 'All_flats'] =  characteristics_df.loc[
        'Minimum price, czk', char_cols].min()
    characteristics_df.loc['Minimum size, m2', 'All_flats'] =  characteristics_df.loc[
        'Minimum size, m2', char_cols].min()
    
    
char_to_show = characteristics_df.T
# to specify columns order
char_to_show = (char_to_show[['Count total', 'Count personal', 'Count new flats',
       'Average price, czk', 'Maximum price, czk', 'Minimum price, czk',
       'Average size, m2', 'Maximum size, m2', 'Minimum size, m2']]
                            .style.format('{:,.0f}')
                            #.applymap('font-weight: bold',
                            #          subset = pd.IndexSlice['All_flats', :])
                            )
# char_to_show = characteristics_df.T[['Count total', 'Count personal', 'Count new flats',
#                                      'Average price, czk', 'Maximum price, czk',
#                                      'Minimum price, czk', 'Average size, m2',
#                                      'Maximun size, m2', 'Minimum size, m2' ]]
# to show dfs
# total df
st.subheader("Total table with flats overview")
df_to_show = (reality_df.copy()
              .drop('district', axis = 1)
              .rename(columns={"price": "Price, czk",
                                               "size": "Size, m2",
                                               "price_per_m2": "Price per m2, czk"
                                                }))
new_names = [i.capitalize() for i in df_to_show.columns]
df_to_show.columns = new_names
st.dataframe(df_to_show.style.format({"Price, czk":"{:,d}",
                                      "Price per m2, czk":"{:,.0f}"}))

# summary df
st.subheader("Summary table")
st.dataframe(char_to_show)

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

# To show price distribution graph
st.subheader("Prices distribution for different flat dispositions [CZK]")
st.plotly_chart(fig, use_container_width=True)


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

st.subheader("Prices of flats based on their size [CZK/m2]")
st.plotly_chart(fig_scatter, use_container_width=True)

import plotly.io as pio


pio.renderers.default='browser'
import plotly.io as pio

# to show picture in spyder directly
#pio.renderers.default='svg'    

        

