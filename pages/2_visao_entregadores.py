import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from haversine import haversine
from PIL import Image
import folium
from streamlit_folium import st_folium


file_ = "dataset/train.csv"
df = pd.read_csv(file_)
#___________________________________________
#funçaoes 
#___________________________________________


def max_min(df , col):
                if col == 'max':
                    valor = df.loc[:,'Delivery_person_Age'].max()
                elif col == 'min':
                    valor = df.loc[:,'Delivery_person_Age'].min()
                return valor


def top_deliveries(df, top_asc):        
                df2 = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID'])
                                                                                    .mean()
                                                                                    .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                                                                                    .reset_index())
                linha_metrop = df2['City'] == 'Metropolitian '
                df_aux01 = df2.loc[linha_metrop, :].head(10)
                df_aux02 = df2.loc[df2['City'] == 'Urban ', :].head(10)
                df_aux03 = df2.loc[df2['City'] == 'Semi-Urban ', :].head(10)

                df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
                return df3











#___________________________________________
#barra lateral 
#___________________________________________
st.header('marketplace - visao entegadores')
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    "Até qual valor?",
    value=pd.Timestamp("2022-04-13").to_pydatetime(),  # Convertendo para datetime do Python
    min_value=pd.Timestamp("2022-02-11").to_pydatetime(),  # Convertendo para datetime do Python
    max_value=pd.Timestamp("2022-04-06").to_pydatetime(),  # Convertendo para datetime do Python
    format='DD-MM-YYYY'
)

st.header(date_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low ' , 'Medium ' , 'High ' , 'Jam '],
    default=['Low ', 'Medium ', 'High ', 'Jam ']
)
st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS")


df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%Y-%m-%d', errors='coerce')

linhas = df['Order_Date'] < date_slider
df=df.loc[linhas,:]

linhas_selc = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selc,:]

st.dataframe(df)


#layout no streamlit

tab1 , tab2 , tab3 = st.tabs(['Visao Gerencial','__','__'])

with tab1:
    with st.container():
        st.markdown("# Orders Metricas")
        col1 , col2 , col3  , col4 = st.columns(4 , gap="large")
        with col1:
            maior = max_min(df , 'max')
            col1.metric("Maior de idade",maior)
        with col2:
            menor = max_min(df , 'min')
            col2.metric("Menor de idade",menor)
        with col3:
            
            melhor = df.loc[:,'Vehicle_condition'].max()
            col3.metric("melhor condiçao de veiculos",melhor)
        with col4:
            
            pior = df.loc[:,'Vehicle_condition'].min()
            col4.metric("pior condiçao de veiculos",pior)


    with st.container():
        st.markdown("""_____""")
        st.title("Avaliaçaoes")
        col1 , col2 = st.columns(2)
        with col1:
            st.markdown("##### Avaliçao media por entregador")
            colus = ['Delivery_person_Ratings', 'Delivery_person_Age']
            gruop = df.loc[:,colus].groupby('Delivery_person_Ratings').mean()
            st.dataframe(gruop)

        with col2:
            st.markdown('##### Avaliacao media por transito')

            df_avg_std_rating_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density')
                                                                                                            .agg({'Delivery_person_Ratings': ['mean', 'std'] }))
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)

            st.markdown("##### Avaliçao media por clima")

            df_avg_std_rating_by_weather = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std'] }))
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
    with st.container():
        st.markdown("""_____""")
        st.title("velociadade dos entregadores") 
        col1 , col2 = st.columns(2)
        with col1:
            st.markdown("##### top entregadores mais rapidos") 
            df3 = top_deliveries(df , top_asc = True)
            st.dataframe(df3)

        with col2:
            st.markdown("##### top entregadores mais lentos")
            df3 = top_deliveries(df , top_asc = False)
            st.dataframe(df3)
