# Basic overview of flats for sale in Prague (streamlit)
#### Video Demo:  [youtube](https://youtu.be/BW6s_93IbwM)
#### Description:
This simple web applications provides basic overview of 1-2-3 room flats currently for sale in Prague as well as shows historical prices development.
Data are downloaded from sreality.cz and czso.cz, they are updated automatically as soon as initial data are refreshed.
It was written in python using libraries such as pandas, requests, streamlit, plotly and BeautifulSoup. As a web framework I have chosen streamlit because it is both simple and efficient. To create interactive graphs I have chosen plotly since it is powerful package, well documented and is compatible with streamlit. 
For an inspiration and to learn streamlit I referred to educational video on youtube by Data Professor [Build 12 Data Science Apps with Python and Streamlit - Full Course](https://www.youtube.com/watch?v=JwSS70SZdyM&t=6368s).

In the first part of the app you can see plotly graph with flat price index development from 2008:
* data are web scrapped from the Czech statistical office (2 excel files) using BeautifulSoup, requests and pandas;
* it reads the most recent historical data from the web.

The second part downloads data from sreality.cz API (using requests library) and displays them into interactive summary tables and graphs:
* sreality API is publicly available but not described so I browsed and estimated parameters;
* I have limited ads for sale only to Prague and 1-2-3bedroom apartments;
* user can select options on the left side, then information on the right side will be updated accordingly;
* tables with basic characteristics include count of ads, sizes and prices statistics;
* graphs below are drawn in plotly, color map corresponds to flat disposition:
    * prices histograms, average price drawn with dashed line;
    * scatterplot of prices of flats based on their size; 
    * barcharts of prices per m2 in different Prague districts.
    
Application overall consists of 3 files:
* get_sreality_data.py includes functions to get API data from sreality.cz into lists of dicts;
* get_price_history.py reads history from czso.cz into pandas dfs.
* sreality.py is the main file of application, that contains initial parameters, references to 2 other files and creating visual side of the application with streamlit.
At first I import all packages and set basic configurations to streamlit, then read price index data and create line charts. Then based on initial parameters and parameters recieved by streamlit as user input I get streamlit API data.

          