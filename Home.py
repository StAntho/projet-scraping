from functions import *
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import iplot
import json

# onglet de la page
st.set_page_config(
    page_icon='🚑',
    page_title='Sport Inventory Injuries',
    layout='wide'
)

# sidebar
st.sidebar.title('Anthony STANIX')
st.sidebar.write('Selenium a été utilisé pour le scraping, afin de pouvoir naviguer sur le site et récupérer les données générés par le js.')
st.sidebar.link_button('📄 Lien vers le site', 'https://www.cbssports.com/')
          
# demande user concernant la récolte des données
st.title('Faire une récolte de données')
sports = {'🏀basketball': 'nba', '🏈football américain': 'nfl', '🏒hockey': 'nhl', '⚾baseball': 'mlb'}
filename = st.text_input("Choisissez un nom de fichier")
sport_choice = st.multiselect("Choisissez une thématique", sports.keys(), default=['🏀basketball'])
n_days = st.slider("Sélectionez le nombre de journées : ",1,300)

# lancement de la récolte
data = {}
if st.button('Lancer la recherche'):
    for sport in sport_choice:
        data = scraping_injuries(sports[sport], n_days, data)

    if filename == '':
        filename = ''.join(str(sport) for sport in sport_choice)
        with open('utiles/'+filename.replace(' ', '_')+'.json','w') as f:
            json.dump(data, f)
    else:
        with open('utiles/'+filename.replace(' ', '_')+'.json','w') as f:
            json.dump(data, f)

if st.checkbox('Voir les données de la récolte'):
    st.write(data)

# Données de la récolte issues de la base de données
st.title('Données de la base')
if DataBase('Scraping_sport_injuries'):
    data_base = DataBase('Scraping_sport_injuries')
    table = st.selectbox("Sélectionner une table", data_base.table)
    df = pd.DataFrame(data_base.select_table(table))

    if st.checkbox("Voir la table par sport"):
        df_sport = st.selectbox("Sélectionner un sport", df.sport.unique())
        df_view_sport = df[df.sport == df_sport]
        # affichage des données en 2 colonnes
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Données de la table pour le '+df_sport)
            st.data_editor(
                df_view_sport,
                column_config={
                "img_team": st.column_config.ImageColumn(
                "Preview Image", help="Streamlit app preview screenshots"
            )})
        with col2:
            injury_location = []
            count = []
            for column in df_view_sport.injury_location.unique():
                injury_location.append(column)

            for item in injury_location:
                count.append(len(df_view_sport[df_view_sport.injury_location == item]))

            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']

            fig = px.pie(df_view_sport, values=count, names=injury_location)

            st.subheader('Répartition des blessures')
            st.plotly_chart(fig)

    if st.checkbox("Voir la table par équipe"):
        df_team = st.selectbox("Sélectionner un équipe", df.team.unique())
        df_view_team = df[df.team == df_team]
        # affichage des données en 2 colonnes
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Données de la table pour le '+df_team)
            st.data_editor(
                df_view_team,
                column_config={
                "img_team": st.column_config.ImageColumn(
                "Preview Image", help="Streamlit app preview screenshots"
            )})
        with col2:
            injury_location = []
            count = []
            for column in df_view_team.injury_location.unique():
                injury_location.append(column)

            for item in injury_location:
                count.append(len(df_view_team[df_view_team.injury_location == item]))

            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']

            fig = px.pie(df_view_team, values=count, names=injury_location)

            st.subheader('Répartition des blessures')
            st.plotly_chart(fig)

# demande user concernant le prompt openAI
st.title('Questionner ChatGPT-3')
prompt = st.text_input('Entrez votre prompt concernant les blessures sportives(nfl, nba, nhl)',
        "Quelles est la blessure ... ?",)

# lancement du prompt openAI
if st.button('Lancer le prompt'):
    st.write(prompt_openAI(prompt))
