# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 21:09:16 2021

@author: annaa
"""

import requests
import math
import re

def get_response(api_url, params, first):
    """To return json response from the url with the given parameters
    if first is tru number of pages will be also returned"""
    response = requests.get(api_url, params = params)
    response.encoding = response.apparent_encoding
    if response.status_code == 200:
        data_reality = response.json()
        number_pages = math.ceil(data_reality['result_size']/(data_reality['per_page'] + 1))
    else:
        print('No response from the page')
    if first:    
        return number_pages, data_reality
    else:
        return data_reality
        
# to get info about flats, list of estates
def create_reality_list(data_reality):
    """To create a list of realities from the given json output"""
    estates_list = data_reality['_embedded']['estates']
    reality_list = []
    disposition_dict = {2: '1kk', 4: '2kk', 6: '3kk'}
    
    # to create list of realities based on estates_list from given page
    for est in estates_list:    
        # if disposition does not correspond purpose group
        if not est['seo']['category_sub_cb'] in disposition_dict.keys():
            continue
        reality_dict = {}
        reality_dict['disposition'] = disposition_dict[est['seo']['category_sub_cb']]
        # name name
        reality_dict['name'] = est['name']
        # price price
        reality_dict['price'] = est['price']
    
        # size
        if "\xa0" in reality_dict['name']:
            reality_dict['size'] = (reality_dict['name']
                    .split("\xa0")[0]
                    .split(' ')[-1])
        else:
            reality_dict['size'] = None
        reality_dict['locality'] = est['locality']
        # part of Prague
        if ',' in est['locality']:
            reality_dict['district'] = est['locality'].split(',')[1].strip()
        else:
            reality_dict['district'] = est['locality'].strip()
        if re.findall('[0-9]*\s', reality_dict['district']):
            reality_dict['district'] = re.sub('[0-9]*\s', '', 
                                              reality_dict['district'])
        
        # (est['seo']['locality'].split('-')[0].capitalize()
        #                              + " " +
        #                              est['seo']['locality'].split('-')[1].capitalize())
        
        # to check if personal ownership
        if 'personal' in est['labelsAll'][0]:
            reality_dict['personal'] = True
        else:
            reality_dict['personal'] = False
            
        if 'new_building' in est['labelsAll'][0]:
            reality_dict['new'] = True
        else:
            reality_dict['new'] = False
            
        reality_dict['id'] = est['hash_id']
        
        reality_list.append(reality_dict)
    
    return reality_list


    
    