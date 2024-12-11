# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 13:31:53 2024

@author: gautnico
"""

# Importation des librairies nécessaires :

import time
import re
import requests
import os
import pandas as pd
from basketball_reference_scraper.teams import get_roster, get_team_ratings, get_team_misc
from basketball_reference_scraper.request_utils import get_wrapper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

#####################################################################################################
#                                 Définition des fonctions                                          #
#####################################################################################################

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
    
    url = f'https://www.basketball-reference.com/teams/{team}/2025.html'  # URL cible pour la saison 2024-2025.

    # Obtenir le contenu de la page :
    response = get_wrapper(url)
    if not response:
        raise ConnectionError('Request to basketball reference failed')

    # Analyser la page HTML :
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trouver le tableau avec l'id "per_game_stats" :
    table = soup.find('table', {'id': 'per_game_stats'})
    if not table:
        raise ValueError('Le tableau "Per Game Table" est introuvable sur la page.')

    # Convertir le tableau HTML en DataFrame :
    df = pd.read_html(str(table))[0]

    # Nettoyage éventuel (supprimer lignes/colonnes inutiles) :
    df = df.dropna(how='all')  # Supprimer les lignes entièrement vides.
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Supprimer les colonnes sans nom.
    df["Rk"] = df["Rk"].fillna(0).astype(int)  # Conversion du type du rang en entier.
    df["Age"] = df["Age"].fillna(0).astype(int)  # Conversion du type de l'âge en entier.

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

    # Configuration de Selenium avec Firefox :
    options = Options()
    options.add_argument("--headless")  # Assurer que le navigateur reste en mode headless (aucune fenêtre ouverte).
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"  # URL cible pour la saison 2024-2025.

    # Charger la page :
    driver.get(url)

    # Trouver le tableau des salaires :
    try:
        table = driver.find_element(By.ID, "salaries2")  # ID du tableau des salaires.
        html = table.get_attribute("outerHTML")  # Récuperer le code HTML du tableau.
    except Exception:
        driver.quit()
        raise ValueError(f"Le tableau 'Salaries' est introuvable pour l'équipe {team}.")

    # Fermer le driver après extraction :
    driver.quit()

    # Convertir le tableau HTML en DataFrame :
    df = pd.read_html(html)[0]

    # Renommer les colonnes en français :
    df.columns = ["Rang", "Joueur", "Salaire"]

    # Nettoyage éventuel (supprimer lignes/colonnes inutiles) :
    df = df.dropna(how="all")  # Suppression des lignes entièrement vides.
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Suppression des colonnes sans nom.

    # Retirer les virgules des salaires pour éviter les conflits avec le format .csv :
    df["Salaire"] = df["Salaire"].replace({",": " "}, regex=True)

    return df


def infos_basiques_equipe(team):
    """
    Récupère les informations de base de l'équipe NBA depuis sa page : record, last game, next game, coach.
    
    Parameters
    ----------
    team : str
        Abréviation de l'équipe (ex. 'LAL' pour Los Angeles Lakers).
    
    Returns
    -------
    df : DataFrame
        DataFrame contenant les informations extraites de la page.
    """

    # Configuration de Selenium avec Firefox :
    options = Options()
    options.add_argument("--headless")  # Assurer que le navigateur reste en mode headless (aucune fenêtre ouverte).
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    url = f"https://www.basketball-reference.com/teams/{team}/2025.html"  # URL cible pour la saison 2024-2025.
    
    # Charger la page :
    driver.get(url)

    # Récupérer le code HTML de la page :
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Fermer le driver après extraction :
    driver.quit()

    # Trouver la div avec la classe "prevnext" :
    prevnext_div = soup.find("div", class_="prevnext")
    
    # Extraire les 4 premières balises <p> après la div "prevnext" :
    infos = []
    if prevnext_div:
        p_tags = prevnext_div.find_all_next("p", limit=4)
        
        # Nettoyer et extraire les textes, remplacer les espaces multiples par des espaces simples :
        infos = [re.sub(r'\s+', ' ', p.text.strip()) for p in p_tags]

    # Diviser chaque ligne par le ":" et ajouter les données dans un dictionnaire :
    data = {}
    for info in infos:
        key, value = info.split(":", 1)   # Diviser chaque ligne par le ":"
        data[key.strip()] = value.strip() # Ajout des données dans le dictionnaire.
    
    # Création d'un DataFrame depuis le dictionnaire :
    df = pd.DataFrame([data])

    # Remplacer les virgules dans les valeurs par des points-virgules :
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
    
    # Obtention du stade de l'équipe :
    serie = get_team_misc(team, 2025)  # Utilisation de la fonction get_team_misc de l'API basketball_reference_scraper.
    arene_df = serie.to_frame().T  # Transformation de la série en df.
    arene_df = arene_df[["ARENA"]]  # Conservation de la colonne "ARENA".
    arene_df.columns = ["Stade"]
    arene_df.index = [0]  # Réinitialisation de l'index pour uniformiser les DataFrame avant la fusion.

    # Informations de l'équipe en lien avec la ligue:
    infos_ligue_equipe_df = get_team_ratings(2025, team)  # Utilisation de la fonction get_team_ratings de l'API basketball_reference_scraper.
    infos_ligue_equipe_df = infos_ligue_equipe_df[["RK", "CONF", "DIV", "W/L%"]]  # Conservation des colonnes pertinentes.
    infos_ligue_equipe_df.columns = ["Classement", "Conférence", "Division", "Pourcentage de victoires"]  
    infos_ligue_equipe_df["Classement"] = infos_ligue_equipe_df["Classement"].fillna(0).astype(int)  # Conversion du type du classement en entier.
    infos_ligue_equipe_df.index = [0]  # Réinitialisation de l'index pour uniformiser les DataFrame avant la fusion.

    # Informations de base de l'équipe :
    infos_base_equipe_df = infos_basiques_equipe(team)  # Utilisation de la fonction infos_basiques_equipe définie précédemment.
    infos_base_equipe_df.columns = ["Record", "Match précédent", "Prochain match", "Coach"]
    infos_base_equipe_df.index = [0]  # Réinitialisation de l'index pour uniformiser les DataFrame avant la fusion.

    # Concaténation des DataFrames :
    df_final = pd.concat([arene_df, infos_ligue_equipe_df, infos_base_equipe_df], axis=1)

    return df_final


# Liste des équipes NBA pour la saison 2024-2025 :
liste_equipes = [
    "CLE", "BOS", "ORL", "NYK", "MIL", "ATL", "MIA", "CHI", "BRK", "IND", 
    "DET", "TOR", "CHO", "PHI", "WAS", "OKC", "HOU", "DAL", "MEM", "LAC", 
    "PHO", "GSW", "DEN", "LAL", "SAS", "MIN", "SAC", "POR", "UTA", "NOP"
]

#####################################################################################################
#                  Création de plusieurs DataFrame pour chaque équipe de la liste                   #
#####################################################################################################
# /!\ Le programme réalisant de nombreuse requête vers le site "https://www.basketball-reference.com/", il y a un risque que ce dernier bloque la récolte de données.
# Si cela arrive, il faudra attendre entre 1h et 2h et modifier le code pour garder uniquement la création des DataFrame inexistant. Cette méthode est la seule solution à ce problème.

# DataFrame pour le roster de l'équipe :
for equipe in liste_equipes:
    print("test")
    # Chemin du fichier .csv :
    chemin_roster = os.path.join("Roster", f"roster_{equipe}.csv")  # Utilisation de la fonction os.path.join pour gérer les chemins de fichiers de manière portable.

    # Vérification de l'existence du fichier .csv :
    if os.path.exists(chemin_roster):
        print(f"Le fichier 'roster_{equipe}.csv' est déjà téléchargé.")
    else:
        print(f"Téléchargement du roster de l'équipe {equipe}...")
        df = get_roster(equipe, 2025)
        df.columns = ["Numéro", "Joueur", "Poste", "Taille (ft)", "Poids (lbs)", "Date de naissance", "Nationalité", "Expérience", "Université"]  # Traduction du nom des colonnes en français.
        df["Numéro"] = df["Numéro"].fillna(0).astype(int)  # Conversion du type du numéro en entier.

        # Création du dossier "Roster" si inexistant et enregistrement du DataFrame dans un fichier .csv :
        os.makedirs("Roster", exist_ok=True)
        df.to_csv(chemin_roster, index=False)
   

# DataFrame pour les statistiques par match et par joueur de l'équipe :
for equipe in liste_equipes:
    # Chemin du fichier .csv :
    chemin_stats = os.path.join("Stats", f"stats_{equipe}.csv")

    # Vérification de l'existence du fichier .csv :
    if os.path.exists(chemin_stats):
        print(f"Le fichier 'stats_{equipe}.csv' est déjà téléchargé.")
    else:
        print(f"Téléchargement des statistiques de l'équipe {equipe}...")
        df = obtenir_stats_equipe(equipe)
        df = df[["Rk", "Player", "Age", "Pos", "G", "3P", "3P%", "2P", "2P%", "FT", "FT%", "TRB", "AST", "PTS"]]  # Conservation des colonnes pertinentes.
        df.columns = ["Rang", "Joueur", "Âge", "Poste", "Matchs", "3 points", "3 points %", "2 points", "2 points %", "Lancer franc", "Lancer franc %", "Rebonds", "Passes décisives", "Points"]  # Traduction du nom des colonnes en français.

        # Création du dossier "Stats" si inexistant et enregistrement du DataFrame dans un fichier .csv :
        os.makedirs("Stats", exist_ok=True)
        df.to_csv(chemin_stats, index=False)


# DataFrame pour le salaire des joueurs de l'équipe :
for equipe in liste_equipes:
    # Chemin du fichier .csv :
    chemin_salaires = os.path.join("Salaires", f"salaires_{equipe}.csv")

    # Vérification de l'existence du fichier .csv :
    if os.path.exists(chemin_salaires):
        print(f"Le fichier 'salaires_{equipe}.csv' est déjà téléchargé.")
    else:
        print(f"Téléchargement des salaires de l'équipe {equipe}...")
        df = salaires_equipe(equipe)

        # Création du dossier "Salaires" si inexistant et enregistrement du DataFrame dans un fichier .csv :
        os.makedirs("Salaires", exist_ok=True)
        df.to_csv(chemin_salaires, index=False)


# DataFrame pour les informations de base de l'équipe :
for equipe in liste_equipes:
    # Chemin du fichier .csv :
    chemin_infos = os.path.join("Infos", f"infos_equipe_{equipe}.csv")

    # Vérification de l'existence du fichier .csv :
    if os.path.exists(chemin_infos):
        print(f"Le fichier 'infos_equipe_{equipe}.csv' est déjà téléchargé.")
    else:
        print(f"Téléchargement des informations de l'équipe {equipe}...")
        df = fusion_df(equipe)

        # Création du dossier "Infos" si inexistant et enregistrement du DataFrame dans un fichier .csv :
        os.makedirs("Infos", exist_ok=True)
        df.to_csv(chemin_infos, index=False)


# Téléchargement des logos des équipes :
for equipe in liste_equipes:
    # Chemin du fichier logo :
    chemin_logo = os.path.join("Logos", f"{equipe}.jpg")

    # Vérification de l'existence du fichier logo :
    if os.path.exists(chemin_logo):
        print(f"Le logo de l'équipe {equipe} est déjà téléchargé.")
    else:
        print(f"Téléchargement du logo de l'équipe {equipe}...")
        image_url = f"https://cdn.ssref.net/req/202411271/tlogo/bbr/{equipe}-2025.png"
        img_data = requests.get(image_url).content  # Récupération des données de l'image.

        # Création du dossier "Logos" si inexistant et enregistrement de l'image dans un fichier .jpg :
        os.makedirs("Logos", exist_ok=True)
        with open(chemin_logo, "wb") as handler:
            handler.write(img_data)

# Message de fin de téléchargement :
print("\nTéléchargement terminé !\n==========================================================\nLes fichiers sont enregistrés dans les dossiers suivants :\n\n- Roster\n- Stats\n- Salaires\n- Infos\n- Logos.")
