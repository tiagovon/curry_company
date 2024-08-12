import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from haversine import haversine
import folium
from streamlit_folium import st_folium


file_ = "train.csv"
try:
    df = pd.read_csv(file_)
except FileNotFoundError:
    st.error("Arquivo não encontrado! Verifique o caminho.")
except Exception as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
#___________________________________________
#funçoes
#___________________________________________
def order_metric(df):
        colus = ['ID','Order_Date']
        group = df.loc[:,colus].groupby('Order_Date').count().reset_index()
        group.columns = ['order_date','qtde_ent']
        fix = px.bar(group , x ='order_date', y ='qtde_ent')
        return fix

def order_traffic(df):
        colus1 = ['ID','Road_traffic_density']
        group1 = df.loc[:,colus1].groupby('Road_traffic_density').count().reset_index()
        group1['perc_ID'] = 100 * ( group1['ID'] / group1['ID'].sum() )
        fix1 = px.pie(group1 , values= 'perc_ID', names ='Road_traffic_density')
        return fix1
def order_city_traffic(df):
                colus2 = ['ID','City','Road_traffic_density']
                group2 = df.loc[:,colus2].groupby(['City','Road_traffic_density']).count().reset_index()
                fix2 = px.scatter(group2, x='City', y='Road_traffic_density', size='ID', color='City')
                st.plotly_chart(fix2, use_container_width=True)
                return fix2


def order_week(df):
            df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['Order_Date'])
            df['week'] = df['Order_Date'].dt.strftime('%U')
            group3 = df.loc[:, ['ID', 'week']].groupby('week').count().reset_index()
            fix = px.line(group3, x='week', y='ID')
            return fix

def order_week_share(df):
            df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['Order_Date'])
            df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
            df_aux01 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
            df_aux02 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
            
            df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
            df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            
            fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
            return fig
def mapa(df):
        colus1 = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        group1 = df.loc[:,colus1].groupby(['City','Road_traffic_density']).median().reset_index()
        group1 = group1[group1['City'] != 'NaN']
        group1 = group1[group1['Road_traffic_density'] != 'NaN']
        map = folium.Map()
        for index, location_info in group1.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']],popup=location_info[['City','Road_traffic_density']]).add_to(map)
        st_folium(map, width=1024, height=600)



#___________________________________________
#Configurando o Streamlit
#___________________________________________
#barra lateral 

st.header('marketplace - visap cliente')
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

#___________________________________________
#layout no streamlit
#___________________________________________

tab1 , tab2 , tab3 = st.tabs(['Visao Gerencial','Visao Tatica','Visao Geografica'])

with tab1:
    with st.container():
        st.markdown("# Orders by Day")
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1 , col2  = st.columns(2)
        with col1:
            st.header("# Orders by Traffic")
            fig = order_traffic(df)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("# Traffic Orders by City")
            fig=order_city_traffic(df)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("# Orders by week")
    with st.container():
        st.header("# Orders by Week")
        fig = order_week(df)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_week_share(df)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("# Geographic Distribution")

    mapa(df)
