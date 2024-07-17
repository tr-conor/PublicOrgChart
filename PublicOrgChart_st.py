
"""
Created on Thu Jul 11 12:44:18 2024

@author: Conor
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyodbc
# from pathlib import Path
# from matplotlib import font_manager
import streamlit as st


driver= '{ODBC Driver 17 for SQL Server}'


prod_params = 'DRIVER='+driver+';SERVER='+st.secrets['MY_SERVER']+';PORT=1433;DATABASE='+st.secrets['MY_DB']+';UID='+st.secrets['MY_USERNAME']+';PWD='+ st.secrets['MY_PASSWORD']
prod_cnxn = pyodbc.connect(prod_params)
prod_cursor = prod_cnxn.cursor()
prod_cursor.fast_executemany = True
 

test_sql = st.secrets['MY_SQL']

test_data = pd.read_sql(test_sql,prod_cnxn)

squad_names = test_data['SquadName']

squad_names = squad_names.drop_duplicates()

squad_names = squad_names.sort_values()

#%% build streamlit

st.set_page_config(
     page_title="Select Players In Squad",
     layout="wide",
     initial_sidebar_state="expanded",    
 )

st.markdown("<font color=#0e9655>TransferRoom</font>", unsafe_allow_html=True)
st.title("Club Organisation Chart Generation")

# st.write(st.experimental_user['email'])
email = st.experimental_user['email']

squad = st.selectbox(
     'Select Squad',
     squad_names)





# %%


mud = test_data[test_data['SquadName']==squad]
mud = mud.reset_index()

squadid = mud.loc[0,'CurrentSquadid']

st.write('Squad Id = '+str(squadid))

G = nx.DiGraph()

nodes = np.arange(0, len(mud)).tolist()

#nodes = mud.loc[:,'ShortName'].tolist()

G.add_nodes_from(nodes)

edges = []

#nds = [7,8,9,10,11,12,13,14]

for n in range(0,len(mud)) :
#for n in nds :
    for i in range(0,len(mud)):
        if mud.loc[n,'role_level'] == mud.loc[i,'role_level'] + 1 and mud.loc[n,'track'] == mud.loc[i,'track']  :
            edges.append(tuple((i,n)))
        elif mud.loc[n,'role_level'] == mud.loc[i,'role_level'] + 1 and np.isnan(mud.loc[n,'track']) == True:
            edges.append(tuple((i,n)))
        elif mud.loc[n,'role_level'] == mud.loc[i,'role_level'] + 1 and np.isnan(mud.loc[i,'track']) == True:
            edges.append(tuple((i,n)))

G.add_edges_from(edges)



pos = {}
labels = {}
colours = []

for n in range(0,len(mud)):
    if mud.loc[n,'xdiv'] ==1:
        x_pos = 5.0
    else:
        x_pos = 0.0+ (mud.loc[n,'xpos']-1)*10/(mud.loc[n,'xdiv']-1)
    y_pos = 12-(( mud.loc[n,'role_level']-1)*3)+1
    # print(x_pos,y_pos)
    pos[n]=(x_pos,y_pos)
    labels[n] = mud.loc[n,'ShortName']+'\n'+mud.loc[n,'RoleDescription']
    
    if mud.loc[n,'department'] == 'Board of Directors' or mud.loc[n,'department'] == 'Management':
        colours.append('#D0D5DD')
    elif mud.loc[n,'department'] == 'Scouting':
        colours.append('#D1E9FF')
    elif mud.loc[n,'department'] == 'Coaching Staff':
        colours.append('#FEE4E2')
    else:
        colours.append('#FEF0C7')
     

# pos = {0:(0, 1), 1:(4, 2), 2:(8, 3)}
       
 #       , 3:(12, (( mud.loc[3,'role_level']-1)*3)+1)
 #       , 4:(16, (( mud.loc[4,'role_level']-1)*3)+1),5:(20, (( mud.loc[5,'role_level']-1)*3)+1), 6:(9, (( mud.loc[6,'role_level']-1)*3)+1), 7:(9, (( mud.loc[7,'role_level']-1)*3)+1),
 # 8:(3, (( mud.loc[8,'role_level']-1)*3)+1), 9:(7, (( mud.loc[9,'role_level']-1)*3)+1), 10:(11, (( mud.loc[10,'role_level']-1)*3)+1), 11:(15, (( mud.loc[11,'role_level']-1)*3)+1)
 # , 12:(5, (( mud.loc[12,'role_level']-1)*3)+1), 13:(10, (( mud.loc[13,'role_level']-1)*3)+1), 14:(15, (( mud.loc[14,'role_level']-1)*3)+1)
 # }

# labels = {0: mud.loc[0,'ShortName'], 1: mud.loc[1,'ShortName'], 2: mud.loc[2,'ShortName'], 3:mud.loc[3,'ShortName'], 4:mud.loc[4,'ShortName'],
#  5: mud.loc[5,'ShortName'], 6:mud.loc[6,'ShortName'], 7: mud.loc[7,'ShortName'],8: mud.loc[8,'ShortName'], 9: mud.loc[9,'ShortName'], 10: mud.loc[10,'ShortName'], 11:mud.loc[11,'ShortName'], 12:mud.loc[12,'ShortName'],
#   13: mud.loc[13,'ShortName'], 14:mud.loc[14,'ShortName']}

fig = plt.figure(1,figsize=(13,10))

# font_path = 'Lato-Regular.ttf'

# font_manager.fontManager.addfont(font_path)

# prop = font_manager.FontProperties(fname = font_path)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams.update({'font.size':7})

nx.draw_networkx(G, pos = pos, labels = labels, arrows = True,
 node_shape = "s", node_color =  'white' #colours
            ,node_size = 1000 ,edge_color = 'black',font_size = 8,font_color = 'black',font_family = 'sans-serif')

# nx.draw_networkx_edge_labels(G, pos = pos, edge_labels={},
#                              font_color='red',font_size=5)

plt.title(mud.loc[0,'SquadName']+" Org Chart")
#plt.show()

st.pyplot(fig)
