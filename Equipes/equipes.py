# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:31:53 2024

@author: gautnico
"""

import time
import re
import requests
import os
from basketball_reference_scraper.teams import get_roster, get_team_ratings, get_team_misc
from basketball_reference_scraper.request_utils import get_wrapper
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup


# Réutilisation et modification de la fonction get_team_stats de l'API basketball_reference_scraper :
def obtenir_stats_equipe(team):
    """
    Récupère les statistiques par match ("Per Game Table") d'une équipe NBA 
    pour la saison 2024-2025 et les enregistre dans un DataFrame.

    Parameters
    ----------
    team : str
        Abréviation de l'équipe (ex. 'LAL' pour Los Angeles Lakers).

    Returns
    -------
    df : DataFrame ou None
        DataFrame contenant les statistiques "Per Game" des joueurs de l'équipe.
        Retourne None si le tableau n'est pas trouvé ou si la requête échoue.

    """
    # URL cible pour la saison 2024-2025
    url = f'https://www.basketball-reference.com/teams/{team}/2025.html'

    # Obtenir le contenu de la page
    response = get_wrapper(url)
    if not response:
        raise ConnectionError('Request to basketball reference failed')

    # Analyser la page HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trouver le tableau avec l'id "per_game_stats"
    table = soup.find('table', {'id': 'per_game_stats'})
    if not table:
        raise ValueError('Le tableau "Per Game Table" est introuvable sur la page.')

    # Convertir le tableau HTML en DataFrame
    df = pd.read_html(str(table))[0]

    # Nettoyage éventuel (supprimer lignes/colonnes inutiles)
    df = df.dropna(how='all')  # Supprimer les lignes entièrement vides
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Supprimer les colonnes sans nom
    df["Rk"] = df["Rk"].fillna(0).astype(int)  # Conversion du rang en entier
    df["Age"] = df["Age"].fillna(0).astype(int)  # Conversion de l'âge en entier

    return df


def salaires_equipe(team):
    """
    Récupère les salaires des joueurs d'une équipe NBA pour la saison 2024-2025
    et les enregistre dans un DataFrame.

    Parameters
    ----------
    team : str
        Abréviation de l'équipe (ex. 'LAL' pour Los Angeles Lakers).

    Returns
    -------
    df : DataFrame ou None
        DataFrame contenant les salaires des joueurs de l'équipe.
        Retourne None si le tableau n'est pas trouvé ou si la requête échoue.
    """
    # Configurer Selenium avec Firefox
    options = Options()
    options.add_argument("--headless")  # Assurer que le navigateur reste en mode headless
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    # URL cible pour la saison 2024-2025
    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
    
    # Charger la page
    driver.get(url)

    # Trouver le tableau des salaires
    try:
        table = driver.find_element(By.ID, "salaries2")  # ID du tableau des salaires
        html = table.get_attribute("outerHTML")  # Obtenir le HTML du tableau
    except Exception:
        driver.quit()
        raise ValueError(f"Le tableau 'Salaries' est introuvable pour l'équipe {team}.")

    # Fermer le driver après extraction
    driver.quit()

    # Convertir le tableau HTML en DataFrame
    df = pd.read_html(html)[0]

    df.columns = ["Rang", "Joueur", "Salaire"]

    # Nettoyage éventuel (supprimer lignes/colonnes inutiles)
    df = df.dropna(how="all")  # Supprimer les lignes entièrement vides
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Supprimer les colonnes sans nom

    # Retirer les virgules des salaires pour éviter les conflits avec le format .csv
    df["Salaire"] = df["Salaire"].replace({",": " "}, regex=True)

    return df


def infos_basiques_equipe(team):
    """
    Récupère les informations de l'équipe NBA depuis sa page : record, last game, next game, coach.
    
    Parameters
    ----------
    team : str
        Abréviation de l'équipe (ex. 'LAL' pour Los Angeles Lakers).
    
    Returns
    -------
    df : DataFrame
        DataFrame contenant les informations extraites de la page.
    """
    # Configurer Selenium avec Firefox
    options = Options()
    options.add_argument("--headless")  # Exécution en mode headless
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    # URL cible pour la saison 2024-2025 de l'équipe
    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"
    
    # Charger la page
    driver.get(url)
    time.sleep(2)  # Attendre que la page se charge

    # Récupérer le HTML de la page
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()  # Fermer le navigateur après récupération du HTML

    # Trouver la div avec la classe "prevnext"
    prevnext_div = soup.find("div", class_="prevnext")
    
    infos = []
    if prevnext_div:
        # Récupérer les 4 premières balises <p> après la div "prevnext"
        p_tags = prevnext_div.find_all_next("p", limit=4)
        
        # Nettoyer et extraire les textes, remplacer les espaces multiples par des points-virgules
        infos = [re.sub(r'\s+', ' ', p.text.strip()) for p in p_tags]

    # Diviser chaque ligne par le ":"
    data = {info.split(":", 1)[0].strip(): info.split(":", 1)[1].strip() for info in infos}
    
    # Créer un DataFrame avec une seule ligne
    df = pd.DataFrame([data])

    # Remplacer les espaces dans les valeurs par des points-virgules
    for col in df.columns:
        df[col] = df[col].replace(",", ";", regex=True)

    return df


def fusion_df(team):
    """
    Fusionne plusieurs DataFrames contenant des informations sur une équipe de NBA pour créer un seul DataFrame
    avec les données suivantes : stade, classement, conférence, division, pourcentage de victoires, record,
    match précédent, prochain match et coach.
    
    Parameters
    ----------
    team : str
        Abréviation de l'équipe (par exemple 'LAL' pour les Los Angeles Lakers).
    
    Returns
    -------
    df_final : DataFrame
        DataFrame contenant les informations fusionnées : stade, classement, conférence, division, pourcentage de 
        victoires, record, match précédent, prochain match et coach de l'équipe NBA spécifiée.
    """

    # Création des DataFrames à fusionner
    
    # Stade de l'équipe :
    serie = get_team_misc(team, 2025)
    arene_df = serie.to_frame().T  # Transformation de la série en df
    arene_df = arene_df[["ARENA"]]  # Colonne à garder
    # Traduction du nom de la colonne en français
    arene_df.columns = ["Stade"]
    arene_df.index = [0]  # Réinitialisation de l'index

    # Informations de l'équipe en lien avec la ligue:
    infos_ligue_equipe_df = get_team_ratings(2025, team)
    infos_ligue_equipe_df = infos_ligue_equipe_df[["RK", "CONF", "DIV", "W/L%"]]  # Colonnes à garder
    # Traduction des noms des colonnes en français
    infos_ligue_equipe_df.columns = ["Classement", "Conférence", "Division", "Pourcentage de victoires"]
    infos_ligue_equipe_df["Classement"] = infos_ligue_equipe_df["Classement"].fillna(0).astype(int)  # Conversion du classement en entier
    infos_ligue_equipe_df.index = [0]  # Réinitialisation de l'index

    # Informations de base de l'équipe :
    infos_base_equipe_df = infos_basiques_equipe(team)
    # Traduction des noms des colonnes en français
    infos_base_equipe_df.columns = ["Record", "Match précédent", "Prochain match", "Coach"]
    infos_base_equipe_df.index = [0]  # Réinitialisation de l'index

    df_final = pd.concat([arene_df, infos_ligue_equipe_df, infos_base_equipe_df], axis=1)

    return df_final


liste_equipes = [
    "CLE", "BOS", "ORL", "NYK", "MIL", "ATL", "MIA", "CHI", "BRK", "IND", 
    "DET", "TOR", "CHO", "PHI", "WAS", "OKC", "HOU", "DAL", "MEM", "LAC", 
    "PHO", "GSW", "DEN", "LAL", "SAS", "MIN", "SAC", "POR", "UTA", "NOP"
]


# Création d'un df pour la liste des joueurs
for equipe in liste_equipes:
    df = get_roster(equipe, 2025)
    # Traduction des noms des colonnes en français
    df.columns = ["Numéro", "Joueur", "Poste", "Taille (ft)", "Poids (lbs)", "Date de naissance", "Nationalité", "Expérience", "Université"]
    df["Numéro"] = df["Numéro"].fillna(0).astype(int)  # Conversion du numéro en entier
    df.to_csv(f"roster_{equipe}.csv", index=False)
   

# Création d'un df pour les statistiques par match et par joueur de l'équipe
for equipe in liste_equipes:
    df = obtenir_stats_equipe(equipe)
    df = df[["Rk", "Player", "Age", "Pos", "G", "3P", "3P%", "2P", "2P%", "FT", "FT%", "TRB", "AST", "PTS"]]  # Colonnes à garder
    # Traduction des noms des colonnes en français
    df.columns = ["Rang", "Joueur", "Âge", "Poste", "Matchs", "3 points", "3 points %", "2 points", "2 points %", "Lancer franc", "Lancer franc %", "Rebonds", "Passes décisives", "Points"]    
    df.to_csv(f"stats_{equipe}.csv", index=False)


# Création d'un df pour les salaires des équipes :
for equipe in liste_equipes:
    df = salaires_equipe(equipe)
    df.to_csv(f"salaires_{equipe}.csv", index=False)


for equipe in liste_equipes:
    df = fusion_df(equipe)
    df.to_csv(f"infos_equipe_{equipe}.csv", index=False)
    

os.mkdir("logo_equipe")
for equipe in liste_equipes:
    image_url = f"https://cdn.ssref.net/req/202411271/tlogo/bbr/{equipe}-2025.png"
    img_data = requests.get(image_url).content
    with open(f'logo_equipe\{equipe}.jpg', "wb") as handler:
        handler.write(img_data)
