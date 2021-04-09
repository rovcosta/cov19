
#LINKS ÚTEIS:
# https://docs.streamlit.io/en/stable/tutorial/create_a_data_explorer_app.html
# https://www.analyticsvidhya.com/blog/2020/10/create-interactive-dashboards-with-streamlit-and-python/
#https://docs.streamlit.io/en/stable/api.html

### CRIAR arquivo requirements.txt 
# pip install pipreqs
# digite no terminal (na pasta onde esta o app) pipreqs ./

### CONECTAR COM GIT
# No terminal: sudo apt install git
# no terminal na pasta do codigo: git init,
# git add . 
#  git commit -m 'first commit'
# git remote add origin "https....gitgi"
# git push origin master


import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from datetime import date as dt

#header = st.beta_container()
#data = st.beta_container()
#features = st.beta_container()

# FAZ DOWNLOAD DO ARQUIVO ZIP E SALVA NA PASTA E CRIA O DF
#@st.cache
def load_data():
    file_path = "https://data.brasil.io/dataset/covid19/caso_full.csv.gz"
    r = requests.get(file_path)
    with open("caso_full.gz",'wb') as f:
        f.write(r.content)
    #select_cols = ['city','city_ibge_code','date','is_last','last_available_confirmed','last_available_deaths','last_available_date','place_type','state','new_confirmed', 'new_deaths']
    df = pd.read_csv('caso_full.gz', compression='gzip', header=0, sep=',', quotechar='"', parse_dates=['date','last_available_date'])
    df['date'] = pd.to_datetime(df['date'],format='%Y%m%d')
    df = df.loc[df['state']=='MT']
    return df
data_mt = load_data()

# variáveis cauculadas
last_day = data_mt['last_available_date'].max().day
last_month = data_mt['last_available_date'].max().month
last_year = data_mt['last_available_date'].max().year
last_date  = data_mt.loc[(data_mt['place_type']=='city')]['last_available_date'].max()
tconf  = data_mt.loc[(data_mt['place_type']=='state')]['last_available_confirmed'].max()
tmort  = data_mt.loc[(data_mt['place_type']=='state')]['last_available_deaths'].max()
txMort = (tmort/tconf)*100
dia_conf  = data_mt.loc[(data_mt['place_type']=='state')&(data_mt['is_last']==True)]['new_confirmed'].max()
dia_mort  = data_mt.loc[(data_mt['place_type']=='state')&(data_mt['is_last']==True)]['new_deaths'].max()


# Cria a tabela de Confirmados e Mortes

def load_table():
    tab = load_data()
    tab = tab.loc[tab['is_last']==True]\
        .groupby('city')[['last_available_confirmed','last_available_deaths','new_confirmed','new_deaths']].max()
    tab.rename({'last_available_confirmed':'Total_casos','last_available_deaths':'Total_mortes','new_confirmed':'Casos_dia','new_deaths':'Mortes_dia'},axis=1, inplace=True)
    tab = tab.sort_values(by='Total_casos', ascending=False)
    return tab
table = load_table()


def grafico_casos():
    g_casos = data_mt.loc[data_mt['place_type']=='state'].copy()
    g_casos.set_index('date', inplace=True)
    g_casos.sort_index(inplace=True)
    g_casos = g_casos.fillna(0)[['new_confirmed']]
    g_casos['Média Móvel'] = g_casos.rolling(window=7).mean()
    g_casos.rename({'new_confirmed':'Casos por dia'},axis=1, inplace=True)
    # gráfico
    sns.set_style('white')
    fig1, ax = plt.subplots(1, figsize=(4,3), dpi=80)
    g_casos.plot(
        color=['#00bfff','#bf00ff'], 
        linewidth = 0.7,
        ax = ax    
        )
    # ax.set_title(f"Casos Confirmados de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
    ax.legend(loc='upper left',fontsize=5, frameon=False)
    ax.set_yticklabels([])
    plt.xticks(rotation='vertical', fontsize=(6)) #define os locais e os rótulos dos xticks
    plt.xlabel(None)
    plt.ylabel(None)

    for s in ['top', 'right','left']: #'bottom', 'left'
        ax.spines[s].set_visible(False) 

    # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
    ax.annotate('Dia:{}/{}/{}\nCasos confirmados:{:.0f}'.format(last_day,last_month,last_year,dia_conf), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=9,color='grey')
    return fig1


def grafico_mortes():
    g_mortes = data_mt.loc[data_mt['place_type']=='state'].copy()
    g_mortes.set_index('date', inplace=True)
    g_mortes.sort_index(inplace=True)
    g_mortes = g_mortes.fillna(0)[['new_deaths']]
    g_mortes['Média movel'] = g_mortes.rolling(window=7).mean()
    g_mortes.rename({'new_deaths':'Mortes por dia'},axis=1, inplace=True)
    #grafico
    sns.set_style('white')
    fig2, ax = plt.subplots(1, figsize=(4,3), dpi=80)
    g_mortes.plot(
        color=['#ffbb33','#ff3333'], 
        linewidth = 0.7,
        ax = ax    
        )
    # ax.set_title(f"Mortes Confirmadas de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
    ax.legend(loc='upper left',fontsize=4)
    ax.set_yticklabels([])
    plt.xticks(rotation='vertical', fontsize=(6)) #define os locais e os rótulos dos xticks
    plt.xlabel(None)
    plt.ylabel(None)

    for s in ['top', 'right','left']: #'bottom', 'left'
        ax.spines[s].set_visible(False) 

    # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
    ax.annotate('Dia:{}/{}/{}\nMortes confirmadas:{:.0f}'.format(last_day,last_month,last_year,dia_mort), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=9,color='grey')
    return fig2


### DISPLAY ON APP ####
# show table 

# st.image('image1.jpg')
# st.markdown('<style>body{background-color: #f2f2f2f2;}</style>',unsafe_allow_html=True)

st.title('VISUAL DADOS - DS  \nCoronavirus MT ')
# st.subheader('Painel de dados e gráficos sobre a evolução da Pandemía do novo Coronavírus no estado de Mato Grosso')

st.write(f'Estado: **MATO GROSSO**  \nÚltima Atualização: **{last_day}/{last_month}/{last_year}**  \nTotal de Casos Confirmados: **{tconf}**  \nTotal de Mortes Confirmadas: **{tmort}**  \nCasos Confirmados Neste Dia: **{dia_conf}**  \nMortes Confirmadas Neste Dia: **{dia_mort}**')

st.markdown('Gráfico 1. Casos Confirmados Por Dia - MT')
mc = grafico_casos()
st.pyplot(mc) #use_container_width=True

st.markdown('Gráfico 2. Mortes Confirmadas Por Dia - MT')
mm = grafico_mortes()
st.pyplot(mm)

st.text("")

st.dataframe(table)#.style.background_gradient(cmap='YlOrRd', low=.1, high=.5))

st.text("\n\n")
st.markdown('Créditos e agradecimentos ao BRASIL.IO e toda acomunidade de programadores organizam e disponibilizam os dados da pandemia em todo território nacional, de forma eficiente, clara e de maneira acessível')




#if st.checkbox('Show raw data'):
#    st.subheader('Raw data')
#    st.write(data)
