
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
# import plotly.graph_objects as go
# import plotly.express as px
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

# variáveis cauculadas ESTADO
last_day = data_mt['last_available_date'].max().day
last_month = data_mt['last_available_date'].max().month
last_year = data_mt['last_available_date'].max().year
last_date  = data_mt.loc[(data_mt['place_type']=='city')]['last_available_date'].max()
tconf  = data_mt.loc[(data_mt['place_type']=='state')]['last_available_confirmed'].max()
tmort  = data_mt.loc[(data_mt['place_type']=='state')]['last_available_deaths'].max()
# txMort = (tmort/tconf)*100
dia_conf  = data_mt.loc[(data_mt['place_type']=='state')&(data_mt['is_last']==True)]['new_confirmed'].max()
dia_mort  = data_mt.loc[(data_mt['place_type']=='state')&(data_mt['is_last']==True)]['new_deaths'].max()


# Cria a tabela de Confirmados e Mortes
@st.cache
def load_table_state():
    tab = data_mt.copy()
    tab = tab.loc[tab['is_last']==True]\
        .groupby('city')[['last_available_confirmed','last_available_deaths','new_confirmed','new_deaths']].max()
    tab.rename({'last_available_confirmed':'Total_casos','last_available_deaths':'Total_mortes','new_confirmed':'Casos_dia','new_deaths':'Mortes_dia'},axis=1, inplace=True)
    tab = tab.sort_values(by='Total_casos', ascending=False)
    return tab
table = load_table_state()


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
        color=['lightgrey','#00bfff'], 
        linewidth = 0.7,
        ax = ax    
        )
    # ax.set_title(f"Casos Confirmados de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
    ax.legend(loc='upper left',fontsize=6, frameon=True)
    #ax.set_yticklabels([])
    plt.xticks(rotation='vertical', fontsize=(6)) #define os locais e os rótulos dos xticks
    #plt.xlabel(None)
    #plt.ylabel(None)

    for s in ['top', 'right','left']: #'bottom', 'left'
        ax.spines[s].set_visible(False) 

    # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
    ax.annotate('Dia:{}/{}/{}\nCasos confirmados:{:.0f}'.format(last_day,last_month,last_year,dia_conf), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=5,color='grey')
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
        color=['lightgrey','#ff3333'], 
        linewidth = 0.7,
        ax = ax    
        )
    # ax.set_title(f"Mortes Confirmadas de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
    ax.legend(loc='upper left',fontsize=6)
    ax.set_yticklabels([])
    plt.xticks(rotation='vertical', fontsize=(6)) #define os locais e os rótulos dos xticks
    plt.xlabel(None)
    plt.ylabel(None)

    for s in ['top', 'right','left']: #'bottom', 'left'
        ax.spines[s].set_visible(False) 

    # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
    ax.annotate('Dia:{}/{}/{}\nMortes confirmadas:{:.0f}'.format(last_day,last_month,last_year,dia_mort), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=5,color='grey')
    return fig2



### DATA CIDADES




###  APP HEADERS
html_temp = """
<div style="background-color:tomato;padding:1.5px">
<h1 style="color:white;text-align:center;">Panorama Coronavirus MT</h1>
</div><br>"""
st.markdown(html_temp,unsafe_allow_html=True)
page_names = ['Estado', 'Município']
page = st.radio('Opções de Visualização', page_names)
st.write('** Visualização por:**', page)

#### POR ESTADO #######

if page == 'Estado':
    st.write(f'Estado  \n**MATO GROSSO**  \nÚltima Atualização  \n**{last_day}/{last_month}/{last_year}**  \nTotal de Casos Confirmados  \n**{tconf}**  \nTotal de Mortes Confirmadas  \n**{tmort}**  \nCasos Confirmados Neste Dia  \n**{dia_conf}**  \nMortes Confirmadas Neste Dia  \n**{dia_mort}**')
    st.text("")
    st.markdown('**Gráfico 1.** Casos Confirmados Por Dia - MT')
    mc = grafico_casos()
    st.pyplot(mc) #use_container_width=True

    st.markdown('**Gráfico 2.** Mortes Confirmadas Por Dia - MT')
    mm = grafico_mortes()
    st.pyplot(mm)

    st.text("")
    st.markdown('**Tabela 1.** Lista de Municípios pela quantidade de casos confirmados e mortes por COVID 19 - MT ')
    st.dataframe(table)#.style.background_gradient(cmap='YlOrRd', low=.1, high=.5))
    st.text("")
    st.text("")
    st.markdown('**Desenvolvido por:**  \n Roverson Costa  \n **Agradecimentos:**  \n BRASIL.IO e toda acomunidade de programadores organizam e disponibilizam os dados da pandemia em todo território nacional, de forma eficiente, clara e de maneira acessível.  \n **Fonte de dados:**  \n [link] https://brasil.io/dataset/covid19/caso_full')
#### POR MUNICÍPIO:    
else:
    #@st.cache
    city = data_mt.loc[(data_mt['place_type']=='city')&(data_mt['date']>='2021-1-1')]
    #cria a lista suspensa com os municípios
    cityList = list(city['city'].drop_duplicates()) 
    result = st.selectbox('Município:',cityList)


    #variáveis de contagem
    c_last_day = city.loc[city['city']==result]['last_available_date'].max().day
    c_last_month = city.loc[city['city']==result]['last_available_date'].max().month
    c_last_year = city.loc[city['city']==result]['last_available_date'].max().year
    c_last_date  = city.loc[city['city']==result]['last_available_date'].max()
    c_tconf  = city.loc[city['city']==result]['last_available_confirmed'].max()
    c_tmort  = city.loc[city['city']==result]['last_available_deaths'].max()
    # txMort = (tmort/tconf)*100
    c_dia_conf  = city.loc[(city['city']==result)&(city['is_last']==True)]['new_confirmed'].max()
    c_dia_mort  = city.loc[(city['city']==result)&(city['is_last']==True)]['new_deaths'].max()


    st.write(f'Município  \n**{result}**  \nÚltima Atualização  \n**{c_last_day}/{c_last_month}/{c_last_year}**  \nTotal de Casos Confirmados  \n**{c_tconf}**  \nTotal de Mortes Confirmadas  \n**{c_tmort}**  \nCasos Confirmados Neste Dia  \n**{c_dia_conf}**  \nMortes Confirmadas Neste Dia  \n**{c_dia_mort}**')

    def gcasos_city():
        g = city.loc[city['city']==result]
        day = g['last_available_date'].max().day
        month = g['last_available_date'].max().month
        year = g['last_available_date'].max().year
        cases_day  = g.loc[(g['is_last']==True)]['new_confirmed'].max()

        g.set_index('date', inplace=True)
        g.sort_index(inplace=True)
        g = g.fillna(0)[['new_confirmed']]
        g['Média Móvel'] = g.rolling(window=7).mean()
        g.rename({'new_confirmed':'Casos por dia'},axis=1, inplace=True)
        # gráfico
        sns.set_style('white')
        fig3, ax = plt.subplots(1, figsize=(4,3), dpi=200)
        
        g.plot(
            color=['lightgrey','#00bfff'], 
            linewidth = 0.7,
            ax = ax    
            )
        # ax.set_title(f"Casos Confirmados de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
        ax.legend(loc='upper left',fontsize=5, frameon=False)
        ax.set_yticklabels([])  

        plt.xticks(rotation='horizontal', fontsize=(5)) #define os locais e os rótulos dos xticks
        plt.xlabel(None)
        plt.ylabel(None)

        for s in ['top', 'right','left']: #'bottom', 'left'
            ax.spines[s].set_visible(False) 

        # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
        ax.annotate('Dia:{}/{}/{}\nCasos confirmados:{:.0f}'.format(day,month,year,cases_day), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=5,color='grey')
        return fig3
    st.markdown(f'**Gráfico 1**. Casos Confirmados Por Dia em {result} - MT')
    gc1 = gcasos_city()
    st.pyplot(gc1)

    ### MORTES####
    def gmortes_city():
        g = data_mt.loc[(data_mt['place_type']=='city')&(data_mt['city']==result)&(data_mt['date']>='2021-1-1')].copy()
        day = g['last_available_date'].max().day
        month = g['last_available_date'].max().month
        year = g['last_available_date'].max().year
        deaths_day  = g.loc[(g['is_last']==True)]['new_deaths'].max()

        g.set_index('date', inplace=True)
        g.sort_index(inplace=True)
        g = g.fillna(0)[['new_deaths']]
        g['Média Móvel'] = g.rolling(window=7).mean()
        g.rename({'new_deaths':'Casos por dia'},axis=1, inplace=True)
        # gráfico
        sns.set_style('white')
        fig4, ax = plt.subplots(1, figsize=(4,3), dpi=80)
        g.plot(
            color=['lightgrey','#ff3333'], 
            linewidth = 0.7,
            ax = ax
            )
        # ax.set_title(f"Mortes Confirmadas de Coronavirus - MT\nDia de referência:{last_day}/{last_month}/{last_year}", fontsize=10)
        ax.legend(loc='upper left',fontsize=6)
        ax.set_yticklabels([])
        plt.xticks(rotation='vertical', fontsize=(6)) #define os locais e os rótulos dos xticks
        plt.xlabel(None)
        plt.ylabel(None)

        for s in ['top', 'right','left']: #'bottom', 'left'
            ax.spines[s].set_visible(False) 

        # ax.annotate(' Fonte: Secretarias Estaduais de Saúde\nConsolidação por Brasil.IO\n*Média Móvel: Média de casos dos últimos 7 dias', xy=(0.5,.07),xycoords='figure fraction',horizontalalignment='center',verticalalignment='top',fontsize=10,color='#2C3E50')
        ax.annotate('Dia:{}/{}/{}\nMortes confirmadas:{:.0f}'.format(day,month,year,deaths_day), xy=(0.09,.83),xycoords='figure fraction',horizontalalignment='left',verticalalignment='top',fontsize=5,color='grey')
        return fig4

    st.markdown(f'**Gráfico 2**. Mortes Confirmadas Por Dia em {result} - MT 2021')
    gc2 = gmortes_city()
    st.pyplot(gc2)

    st.text("")
    st.markdown('**Tabela 1.** Lista de Municípios pela quantidade de casos confirmados e mortes por COVID 19 - MT ')
    st.dataframe(table)#.style.background_gradient(cmap='YlOrRd', low=.1, high=.5))
    st.text("")
    st.text("")
    st.markdown('**Desenvolvido por:**  \n Roverson Costa  \n **Agradecimentos:**  \n BRASIL.IO e toda acomunidade de programadores organizam e disponibilizam os dados da pandemia em todo território nacional, de forma eficiente, clara e de maneira acessível.  \n **Fonte de dados:**  \n [link] https://brasil.io/dataset/covid19/caso_full')

### TABELA
    # def load_table_city():
    #     c = city.loc[city['city']==result]
    #     c = c.groupby('last_available_date')[['last_available_confirmed','last_available_deaths','new_confirmed','new_deaths']].max().reset_index()
    #     c.rename({'last_available_date':'Data','last_available_confirmed':'Total_casos','last_available_deaths':'Total_mortes','new_confirmed':'Casos_dia','new_deaths':'Mortes_dia'},axis=1, inplace=True)
    #     c = c.set_index('Data')
    #     c = c.sort_values(by='Total_casos', ascending=False)
    #     return c
    # city_table = load_table_city()
    # st.text("")
    # st.dataframe(city_table)

   



#https://docs.streamlit.io/en/stable/api.html?highlight=container#display-charts






#if st.checkbox('Show raw data'):
#    st.subheader('Raw data')
#    st.write(data)
