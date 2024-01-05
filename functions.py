from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sqlalchemy as db
import streamlit as st
import random
import openai
import time


class DataBase():
    def __init__(self, name_database='database'):
        self.name = name_database
        self.url = f"sqlite:///{name_database}.db"
        self.engine = db.create_engine(self.url)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
        self.table = self.engine.table_names()


    def create_table(self, name_table, **kwargs):
        colums = [db.Column(k, v, primary_key = True) if 'id_' in k else db.Column(k, v) for k,v in kwargs.items()]
        db.Table(name_table, self.metadata, *colums)
        self.metadata.create_all(self.engine)
        print(f"Table : '{name_table}' are created succesfully")

    def read_table(self, name_table, return_keys=False):
        table = db.Table(name_table, self.metadata, autoload=True, autoload_with=self.engine)
        if return_keys:table.columns.keys()
        else : return table


    def add_row(self, name_table, **kwarrgs):
        name_table = self.read_table(name_table)

        stmt = (
            db.insert(name_table).
            values(kwarrgs)
        )
        self.connection.execute(stmt)
        print(f'Row id added')


    def delete_row_by_id(self, table, id_):
        name_table = self.read_table(name_table)

        stmt = (
            db.delete(name_table).
            where(player.c.id_ == id_)
            )
        self.connection.execute(stmt)
        print(f'Row id {id_} deleted')

    def select_table(self, name_table):
        name_table = self.read_table(name_table)
        stm = db.select([name_table])
        return self.connection.execute(stm).fetchall()

def scraping_injuries(theme='nba', n_days=3, data={}):

    # 1  Connexion à la base de données
    database = DataBase('Scraping_sport_injuries')

    # 2 Création d'une table
    if 'players-injured' not in database.table:
        database.create_table(
            'players-injured',
            player=db.String,
            sport=db.String,
            img_team=db.String,
            team=db.String,
            injury_location=db.String,
            injury_date=db.String,
        )

    driver = Chrome()
    driver.get(f"https://www.cbssports.com/{theme}/injuries/daily/")
    # reject cookies
    driver.find_element(By.ID, "onetrust-reject-all-handler").click()
    days = driver.find_elements(By.CLASS_NAME, "TableBaseWrapper")
    
    for day in range(0, n_days):
        try:
            time.sleep(1)
            # day
            journey = days[day].find_element(By.TAG_NAME, "h4").text
            # tr per day
            trs = days[day].find_elements(By.TAG_NAME, "tr")
            for tr in range(1, len(trs)):
                time.sleep(3)
                # img team
                try:
                    img_team = trs[tr].find_element(By.CLASS_NAME, "TeamLogo-image").get_attribute("src")
                except:
                    None
                # team
                try:
                    team = trs[tr].find_elements(By.TAG_NAME, "td")[0].text
                except:
                    None
                # player
                try:
                    player = trs[tr].find_elements(By.TAG_NAME, "td")[1].text
                except:
                    None
                # injury location
                try: 
                    injury_location = trs[tr].find_elements(By.TAG_NAME, "td")[3].text
                except:
                    None
                # sport
                if theme == 'nba':
                    sport = 'basketball'
                elif theme == 'nfl':
                    sport = 'football américain'
                elif theme == 'mlb':
                    sport = 'baseball'
                else:
                    sport = 'hockey'

                # add row in db
                if player not in database.select_table('players-injured'):        
                    database.add_row('players-injured', player=player, sport=sport, img_team=img_team, team=team, injury_location=injury_location, injury_date=journey)
                # create dict
                data[str(random.randint(10000, 1000000))] = {
                    'player': player,
                    'sport': sport,
                    'img_team': img_team,
                    'team': team,
                    'injury_location': injury_location,
                    'injury_date': journey
                }
        except:
            print(f'Récolte de données terminée')
            driver.quit()
            return data 
    print(f'Récolte de données terminée')
    driver.quit()
    return data  

def prompt_openAI(prompt):
    openai.api_key = ""
    reponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
            "content": f"Quelles est la blessure "+ prompt +" ?"},
        ],
        max_tokens=100,
        temperature=0.9,
    )

    return reponse['choices'][0]['message']["content"]