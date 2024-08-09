import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from haversine import haversine
from PIL import Image
import numpy as np 
import folium
from streamlit_folium import st_folium


file_ = "C:\\Users\\Tiago\\OneDrive\\Documentos\\repos\\ftc_progama\\dataset\\train.csv"
df = pd.read_csv(file_)

#___________________________________________
#funçoes
#___________________________________________


#def haversine(df):
           # cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
           # df['distancia'] = df.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
           # avg_distance = np.round(df['distancia'].mean(),2)
           # return avg_distance

def avg_std_traffic(df, yes_no , avg_std):
            df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == yes_no, avg_std],2)
            return df_aux
def avg_std(df):
                    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
                    df_aux.columns = ['avg_time', 'std_time']
                    df_aux = df_aux.reset_index()
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Control', x=df_aux['City'],y=df_aux['avg_time'],error_y=dict(type='data', array=df_aux['std_time'])))
                    fig.update_layout(barmode='group')
                    return fig























#barra lateral 

st.header('marketplace - visao Restaurante')
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

tab1 , tab2 , tab3 = st.tabs(['Visao Restaurante','__','__'])

with tab1:
    with st.container():
        cols1, cols2 , cols3 , cols4 , cols5 , cols6 = st.columns(6) 

        with cols1:
            delivery_unique = len(df['Delivery_person_ID'].unique())
            cols1.metric("Entregadores unicos",delivery_unique)
        with cols2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distancia'] = df.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round(df['distancia'].mean(),2)
            #avg_distance = haversine(df)
            cols2.metric("Distancia media",avg_distance)

        with cols3:
            df_aux = avg_std_traffic( df,'Yes ', 'avg_time')
            cols3.metric('AVG COM FESTIVAL', df_aux)
        

        with cols4:
            df_aux = avg_std_traffic(df, 'Yes ' ,'std_time')
            cols4.metric('STD COM FESTIVAL', df_aux)
        with cols5:
            df_aux = avg_std_traffic(df, yes_no ='No ', avg_std = 'avg_time')
            cols5.metric('AVG SEM FESTIVAL', df_aux) 
        with cols6:
            df_aux = avg_std_traffic(df, yes_no ='No ', avg_std = 'std_time')
            cols6.metric('STD SEM FESTIVAL', df_aux) 



    with st.container():
            couls1 , couls2 =  st.columns(2)
            with couls1:
                fig = avg_std(df)
                st.plotly_chart(fig, use_container_width=True)
            with couls2:
                cols = ['City', 'Time_taken(min)', 'Type_of_order']
                gruop = df.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
                gruop.columns = ['avg_time', 'std_time']
                gruop = gruop.reset_index()
                st.dataframe(gruop)
        
    with st.container():
        st.markdown("""_____""")
        cols1 ,cols2 =  st.columns(2)
        with cols1:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distance'] = df.loc[:, cols].apply(lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)

            

        with cols2:

            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                  color='std_time', color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width=True)
