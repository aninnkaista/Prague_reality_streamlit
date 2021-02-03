# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 20:34:24 2021

@author: annaa
"""



import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import googletrans
from googletrans import Translator


periods = pd.period_range(start = '1/1/2015', end = pd.Timestamp.today(), 
                        freq = 'M')
url_date = str(periods[5]) + '-01'

url = 'https://www.ote-cr.cz/cs/statistika/typove-diagramy-dodavek-plynu/teploty?date=' + url_date
temp = pd.read_html(url, index_col = 0, decimal = ',', thousands = '', encoding='utf-8')[0]
locations = [i.split(' - ')[-1].strip() for i in temp.T.columns[1:]]

temp_df = temp.T

temp_df.index = pd.date_range(start = periods[5].to_timestamp(freq = 'D', how = 's'), 
                              end = periods[5].to_timestamp(freq = 'D', how = 'e'), 
                              freq = 'D', normalize=True)
temp_df = temp_df.dropna(how = 'all', axis = 1)
temp_df.iloc[:, 0:2].plot()

temp_df.describe()

translator = Translator()
translator.translate('kniha', src = 'cs', dest = 'en')
    
for el in locations:
    print(el)
    print(translator.translate(el, src = 'cs', dest = 'en' ))