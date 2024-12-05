import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

def extraire_infos_equipe(team):
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

# Exemple d'utilisation
df_lakers = extraire_infos_equipe("LAL")  # Récupérer les infos des Lakers
print(df_lakers)  # Affiche le DataFrame



df_lakers.to_csv("infos_basiques.csv", index=False)
