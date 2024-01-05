import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(
    page_icon='🗃️',
    page_title='Archive csv',
    layout='wide'
)

st.sidebar.title('Anthony STANIX')
    
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

last_scraping = {file.replace('_', ' ').replace('.json', ''): file for file in os.listdir('utiles') if file!= '.json'}
key_article = st.selectbox('Choisissez une collect : ', last_scraping)
df = pd.read_json('utiles/'+last_scraping[key_article]).T
nb_article = st.slider("Nombre d'article à afficher ?", 1, 500)

for i in range(nb_article):
    try:
        col1, col2 = st.columns(2)

        with col1: st.image(df.iloc[i].image)
        with col2:st.write(df.iloc[i].title)
    except:
        break


csv = convert_df(df)

st.sidebar.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=key_article+'.csv',
    mime='text/csv',
)

st.dataframe(df)