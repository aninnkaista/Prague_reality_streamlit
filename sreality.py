# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 21:33:17 2021

@author: annaa
"""

import streamlit as st
from get_sreality_data import get_response, create_reality_list
import pandas as pd
from get_price_history import download_prices_history
import time

import plotly.graph_objects as go
from plotly.subplots import make_subplots

colors_map = {'1kk': '#008B8B', '2kk': '#8B008B', '3kk': '#1D0FE8'}
api_url = "https://www.sreality.cz/api/cs/v2/estates"

# ----------------------------------------Basic configs------------------------------------------------------------------
st.set_page_config(layout="wide")

st.markdown("# Basic overview of flats for sale in Prague")

expander = st.beta_expander("Sources and inspirations")
expander.markdown("""
* Server for realities search in the Czech republic [sreality.cz](https://www.sreality.cz/);
* Czech statistical office [czso.cz](https://www.czso.cz/csu/czso/indexy-realizovanych-cen-bytu-4-ctvrtleti-2020);
* Python packages and corresponding libraries such as pandas, requests, streamlit, plotly and BeautifulSoup;
* Educational video on youtube by Data Professor [Build 12 Data Science Apps with Python and Streamlit - Full Course] (https://www.youtube.com/watch?v=JwSS70SZdyM&t=6368s)
"""
                  )

# ---------------------------------------Historical data-----------------------------------------------------------------
# to get history prices data and draw their graphs
st.markdown("### Historical development")


@st.cache
def draw_history_graphs():
    """To draw index development graph"""
    prices_index_total = download_prices_history()
    fig_line = go.Figure(layout={'height': 500, 'legend': {'valign': 'top', 'orientation': 'v'},
                                 'margin': {'l': 20, 'r': 20, 't': 20, 'b': 20}},
                         )
    i = 1
    for name, df in prices_index_total.items():
        fig_line.add_trace(go.Scatter(name=name,
                                      x=df.index,
                                      y=df[df.columns[0]],
                                      # marker_color=colors_map[disposition_list[i]],
                                      opacity=0.7, mode='lines'))
        i += 1
    fig_line.update_yaxes(gridcolor="rgba(232,232,232, 0.3)")
    fig_line.update_xaxes(tickangle=30, showgrid=False, tickmode='auto', nticks=int(len(df.index) / 3))
    return fig_line


# To show bar chart
st.markdown("#### Flat price index from the Czech statistical office")
st.plotly_chart(draw_history_graphs(), use_container_width=True, config=dict(displayModeBar=False))
st.markdown("### Summary of information about 1kk, 2kk and 3kk flats sales prices from sreality.cz")

# ------------------------------------------SREALITY data----------------------------------------------------------------

# parameters to get data from sreality
params_init = {
    # flat
    "category_main_cb": "1",
    # size, 1kk, 2kk and 3kk
    "category_sub_cb": "2%7C4%7C6",
    "category_type_cb": "1",
    "locality_region_id": "10",  # Prague
    "page": "1"
}

# Page layout
col_1 = st.sidebar

col_1.header("User options for sreality data")

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


# Get data from sreality

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
        # to sleep before next API request
        time.sleep(0.2)
        data_reality = get_response(api_url, params, False)

    init_reality_df = pd.DataFrame(data=total_reality_list)
    init_reality_df["size"] = pd.to_numeric(init_reality_df["size"])
    init_reality_df.insert(4, 'price_per_m2', init_reality_df['price'] / init_reality_df['size'])

    return init_reality_df


init_reality_df = get_all_data(api_url, params_1)

# Sidebar settings

# select if personal
personal_char = col_1.checkbox("If only personal ownership", False)
# select if new
new_char = col_1.checkbox("If only new flat", False)

# slider for price
min_value = 1000000
max_value = 50000000
price_range = col_1.slider("Price range", min_value, max_value,
                           (min_value, max_value),
                           step=500000, format='%d')

# slider for size
min_value = 10
max_value = 300
size_range = col_1.slider("Size range, m2", min_value, max_value, (min_value, max_value),
                          step=5, format='%d')

# multiple select 1kk, 2kk, 3kk
disposition_options = ['1kk', '2kk', '3kk']
disposition_list = col_1.multiselect("Select relevant flat dispositions",
                                     disposition_options,
                                     disposition_options)

# multiple select districts of Prague
district_list = sorted((init_reality_df[
    ~init_reality_df['district'].str.match('Praha(-)?(Praha)?(\d)*$')]
                       )['district'].unique())
# to shorten the name

selected_districts = col_1.multiselect("Select Prague districts",
                                       district_list,
                                       district_list)

# to filter reality_df according to the sidebar parameters

filt_reality_df = init_reality_df.loc[
    # price
    (init_reality_df.price >= price_range[0]) &
    (init_reality_df.price <= price_range[1]) &
    # size
    (init_reality_df['size'] >= size_range[0]) &
    (init_reality_df['size'] <= size_range[1]) &
    # disposition
    (init_reality_df.disposition.isin(disposition_list)) &
    # districts
    (init_reality_df.district.isin(selected_districts))
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

# Creating summary table

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

    characteristics['Average price per m2, czk'] = round(df.price_per_m2.mean(), 0)

    characteristics['Average size, m2'] = round(df['size'].mean(), 2)
    characteristics['Maximum size, m2'] = round(df['size'].max(), 2)
    characteristics['Minimum size, m2'] = round(df['size'].min(), 2)

    total_characteristics[disp] = characteristics

characteristics_df = pd.DataFrame(total_characteristics)
char_cols = characteristics_df.columns
if len(char_cols) > 1:
    characteristics_df['All_flats'] = characteristics_df.sum(axis=1)

    characteristics_df.loc['Average price, czk', 'All_flats'] = round(characteristics_df.loc[
                                                                          'Average price, czk', char_cols].mean(), 0)
    characteristics_df.loc['Average price per m2, czk', 'All_flats'] = round(characteristics_df.loc[
                                                                                 'Average price per m2, czk', char_cols].mean(),
                                                                             0)
    characteristics_df.loc['Average size, m2', 'All_flats'] = round(characteristics_df.loc[
                                                                        'Average size, m2', char_cols].mean(), 2)
    characteristics_df.loc['Maximum price, czk', 'All_flats'] = characteristics_df.loc[
        'Maximum price, czk', char_cols].max()
    characteristics_df.loc['Maximum size, m2', 'All_flats'] = characteristics_df.loc[
        'Maximum size, m2', char_cols].max()
    characteristics_df.loc['Minimum price, czk', 'All_flats'] = characteristics_df.loc[
        'Minimum price, czk', char_cols].min()
    characteristics_df.loc['Minimum size, m2', 'All_flats'] = characteristics_df.loc[
        'Minimum size, m2', char_cols].min()

char_to_show = characteristics_df.T

cols_size_count = ['Count total', 'Average size, m2', 'Maximum size, m2', 'Minimum size, m2']
cols_prices = ['Average price per m2, czk', 'Average price, czk', 'Maximum price, czk', 'Minimum price, czk', ]
# to specify columns order
char_to_show_1 = (char_to_show[cols_size_count].style.format('{:,.0f}'))
char_to_show_2 = (char_to_show[cols_prices].style.format('{:,.0f}'))

# ------------------------Show tables in the app

# st.markdown("#### Total table with flats overview")
# df_to_show = (reality_df.copy()
#               .drop('district', axis=1)
#               .rename(columns={"price": "Price, czk",
#                                "size": "Size, m2",
#                                "price_per_m2": "Price per m2, czk"
#                                }))
# new_names = [i.capitalize() for i in df_to_show.columns]
# df_to_show.columns = new_names
# st.dataframe(df_to_show.style.format({"Price, czk": "{:,d}",
#                                       "Price per m2, czk": "{:,.0f}"}))

# summary df
st.markdown("#### Basic characteristics")
st.dataframe(char_to_show_1)
st.dataframe(char_to_show_2)

# graph of price distribution for each dispozition
fig = make_subplots(rows=1, cols=len(disposition_list),
                    subplot_titles=[i + " Prices, CZK" for i in disposition_list])

for i in range(len(disposition_list)):
    cur_x = reality_df.loc[
        reality_df.disposition == disposition_list[i]].price
    fig.add_trace(go.Histogram(x=cur_x,
                               marker_color=colors_map[disposition_list[i]]),
                  row=1, col=i + 1)
    fig.add_vline(
        x=cur_x.mean(),
        line_color="Red", line_dash="dash",
        layer="above", line_width=2,
        row=1, col=i + 1)
    fig.update_yaxes(gridcolor="rgba(232,232,232, 0.3)")

fig.update_layout(showlegend=False,
                  height=500,
                  margin={'l': 50, 'r': 20, 't': 20, 'b': 20})

# To show price distribution graph
st.markdown("#### Prices distribution for different flat dispositions [CZK]")
st.plotly_chart(fig, use_container_width=True)

# graph of size/price coloring by dispozition
fig_scatter = go.Figure(data=go.Scatter(
    x=reality_df['size'], y=reality_df.price,
    marker_color=reality_df.disposition.map(colors_map),
    mode='markers',
    text=reality_df.name,
    showlegend=False,
    opacity=0.9
))

fig_scatter.update_layout(
    # title_text = "Prices of flats based on their size",
    height=500, yaxis={"title": "Price [CZK]", "showgrid": False},
    xaxis={"title": "Size, m2", "showgrid": False},
    margin={'l': 20, 'r': 20, 't': 20, 'b': 20})

st.markdown("#### Prices of flats based on their size [CZK/m2]")
st.plotly_chart(fig_scatter, use_container_width=True)

# for bar chart
price_district_raw = reality_df.groupby(['district', 'disposition']
                                        )['price_per_m2'].mean().reset_index()

price_district = (price_district_raw.loc[~price_district_raw['district'].str.match('Praha(-)?(Praha)?(\d)*$')]
                  .sort_values(['disposition', 'price_per_m2'])
                  )
fig_bar = make_subplots(rows=len(disposition_list), cols=1,
                        subplot_titles=[i + " average m2 prices [CZK]" for i in disposition_list],
                        vertical_spacing=0.07)
for i in range(len(disposition_list)):
    fig_bar.add_trace(go.Bar(name=disposition_list[i],
                             x=price_district.loc[price_district.disposition == disposition_list[i], 'district'],
                             y=price_district.loc[
                                 price_district.disposition == disposition_list[i], 'price_per_m2'].round(-3),
                             marker_color=colors_map[disposition_list[i]],
                             opacity=0.7),
                      row=i + 1, col=1)
    fig_bar.update_yaxes(title_text="Price per m2, CZK", row=i + 1, col=1, gridcolor="rgba(232,232,232, 0.3)")
    fig_bar.update_xaxes(tickangle=30, row=i + 1, col=1, showgrid=False)

fig_bar.update_layout(
    # title_text = "Prices of flats based on their size",
    height=500 * len(disposition_list),
    margin={'l': 50, 'r': 20, 't': 20, 'b': 20}
)

# to show bar chart
st.markdown("#### Prices per m2 in different Prague districts [CZK]")
st.plotly_chart(fig_bar, use_container_width=True)


st.markdown("--------------------------------------------------")
st.markdown("_Created by Anna Istomina from Prague, the Czech Republic_")
