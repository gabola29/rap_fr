# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 18:43:19 2022

@author: Gabriel Letty
"""

import networkx as nx
import network_tools.network_calculation as nc
import pandas as pd
import json

# on charge le reseau : 
    
data = nx.read_gml("./data/reseau_version_finale.gml")

# on calcule les stats:

dataclean_info = nc.overall_calculations(data)  

dataclean_indiv = nc.network_measures_to_dataframe(data, include_node_value=False)    
    
dist_bary_clean = nc.distance_to_barycenter_for_each_node(data)   

# on exporte tout ça pour pouvoir le mettre dans streamlit 

dataclean_indiv.to_csv('data/network_indiv_metrics.csv', sep=',', encoding='utf8', index=False)

# le reste en json, mais on ne mettra pas sur mongo

with open('data/overall_metrics.json', 'w',encoding='utf-8') as outfile:
    json.dump(dataclean_info, outfile,ensure_ascii=False, indent=4)
    
with open('data/distance_barycenter.json', 'w',encoding='utf-8') as outfile:
    json.dump(dist_bary_clean, outfile,ensure_ascii=False, indent=4)
