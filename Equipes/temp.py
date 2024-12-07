import time
import re
from basketball_reference_scraper.teams import get_roster, get_team_ratings, get_team_misc
from basketball_reference_scraper.request_utils import get_wrapper
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup


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
    infos_ligue_equipe_df["Classement"] = infos_ligue_equipe_df["Classement"].astype(int)  # Conversion du classement en entier
    infos_ligue_equipe_df.index = [0]  # Réinitialisation de l'index

    # Informations de base de l'équipe :
    infos_base_equipe_df = infos_basiques_equipe(team)
    # Traduction des noms des colonnes en français
    infos_base_equipe_df.columns = ["Record", "Match précédent", "Prochain match", "Coach"]
    infos_base_equipe_df.index = [0]  # Réinitialisation de l'index

    df_final = pd.concat([arene_df, infos_ligue_equipe_df, infos_base_equipe_df], axis=1)

    return df_final

print(fusion_df("LAL"))
df = fusion_df("LAL")
df.to_csv("teeeeest.csv", index=False)