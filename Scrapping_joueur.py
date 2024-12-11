# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:26:54 2024

@author: Manoubi
"""
# Importer les modules pour faire le scrapping depuis BeautifulSoup :
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

# Importer les fonctions de l'API qu'on va utiliser plus tard :
from lookup import lookup
from players import get_player_suffix,get_game_logs,get_player_splits,get_player_headshot

# Importer les modules pour faire le scrapping depuis Selenium :
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

# Importer les modules pour faire les graphiques
import matplotlib.pyplot as plt
import pandas as pd

def menu_joueur():
    dico_joueurs = {"1":"Stephen Curry",
                   "2":"Lebron James", 
                   "3":"Derrick Rose",
                   "4":"Kevin Durant",
                   "5":"Kawhi Leonard",
                   "6":"Nikola Jokic",
                   "7":"Luka Dončić",
                   "8":"Devin Booker",
                   "9":"Jayson Tatum",
                   "10":"Donnovan Mitchell"
                   }
    
    for numero,joueur in dico_joueurs.items():
        print(numero,": ",joueur)
    Choix = input('Donner votre choix de joueur entre 1 et 10: ')
    if Choix not in dico_joueurs.keys():
        Choix = input('redonner un choix valide : ')
    scrapping_joueur(dico_joueurs[Choix])
    return

def creation_dossier(chemin_dossier, nom_dossier):
    """
    Crée un dossier s'il n'existe pas.
    """
    
    if not os.path.exists(nom_dossier):
        os.mkdir(f"{chemin_dossier}\{nom_dossier}")
    return f"{chemin_dossier}\{nom_dossier}"

def get_stats(player_name):
    try:
        # Trouver l'url de la page du joueur
        name = lookup(player_name, ask_matches = True)
        suffix = get_player_suffix(name)
        url = "https://www.basketball-reference.com"+str(suffix)
        
        # Envoyer une requête à la page sports-reference
        response = requests.get(url)
        response.raise_for_status()  # Vérifiez si la demande a réussi.
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

    try:
        # Lire l'HTML avec BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Trouver la table
        table = soup.find_all("table", {"id": "per_game_stats"})

        # Créer un Dataframe avec la table 
        df = pd.read_html(StringIO(str(table)))[0]
        
        # Garder que les colonnes qu'on a besoin
        columns_to_keep = ['Season', 'Age', 'Team', 'Lg', 'Pos', 'G', 'FT%', '3P', '2P', '2P%', '3P%', 'FT', 'TRB', 'AST', 'PTS', 'Awards']
        df = df[columns_to_keep]
        
        # Identifier la deuxième table des totaux et la supprimer (table gris)
        for idx, row in df.iterrows():
            if pd.isna(row['Season']) or not str(row['Season']).startswith(('1', '2')):  # Vérifiez les valeurs non valides ou non saisonnières
                break
        df = df.iloc[:idx]
        
        # Renommer les colonnes en français
        df.columns = [
            'Saison', 'Âge', 'Équipe', 'Ligue', 'Position', 'Matchs joués', 'Pourcentage de LF', '3 Points', '2 Points', 'Pourcentage de 2P',
            'Pourcentage de 3P', 'Lancers Francs', 'Rebonds', 'Passes Décisives', 'Moyenne des Points', 'Récompenses'
        ]

        
    except Exception as e:
        print(f"Error parsing the HTML or reading the table: {e}")
        return None
    return df
  
    
def get_game_highs(player_name):
    try:
        # Trouver l'url de la page du joueur
        name = lookup(player_name, ask_matches = True)
        suffix = get_player_suffix(name)
        url = "https://www.basketball-reference.com"+str(suffix)
        
        # Envoyer une requête à la page sports-reference
        response = requests.get(url)
        response.raise_for_status()  # Vérifiez si la demande a réussi.
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    
    try:
        # Configurer les options pour le navigateur Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Exécuter Chrome en mode sans interface graphique (headless)
        options.add_argument('--disable-gpu')  # Désactiver l'utilisation du GPU pour éviter certains problèmes
        options.add_argument('--no-sandbox')  # Désactiver le mode sandbox pour améliorer la compatibilité
        
        # Initialiser le navigateur Chrome avec les options configurées
        driver = webdriver.Chrome(options=options)
        
        # Charger la page web
        driver.get(url)
        
        # Localiser la table contenant les données souhaitées
        table = driver.find_element(By.ID, 'highs-reg-season')
        html_content = table.get_attribute('outerHTML') # Extraire le contenu HTML de la table
        
        # Analyser le contenu de la table avec Pandas
        df = pd.read_html(html_content)[0]
        
        # Supprimer les lignes où tous les éléments sont des valeurs manquantes (NaN)
        df = df.dropna(how='all')

        # Renommer les colonnes
        df.columns = ['Saison', 'Âge', 'Équipe', 'Ligue', 'Minutes jouées',
                      'Tirs réussis', 'Tirs tentés','3 Points réussis',
                      '3 Points tentés', '2 Points réussis', '2 Points tentés',
                      'Lancers francs réussis', 'Lancers francs tentés',
                      'Rebonds offensifs', 'Rebonds défensifs',
                      'Rebonds totaux', 'Passes décisives', 'Interceptions', 
                      'Contres', 'Ballons perdus', 'Fautes', 'Points',
                      'Évaluation (GmSc)']
        
        # Supression du tableau gris (tableau des totals)
        df = df[~df['Saison'].str.contains("Career", na=False)]
        df = df[~df['Saison'].str.contains("Seasons", na=False)]
        
        # Garder que les colonnes qu'on a besoin
        colonnes = ['Saison', 'Âge', 'Équipe', 'Ligue', 'Minutes jouées',
                      'Tirs réussis','3 Points réussis',
                      '2 Points réussis',
                      'Lancers francs réussis',
                      'Rebonds offensifs', 'Rebonds défensifs',
                      'Rebonds totaux', 'Passes décisives', 'Interceptions', 
                      'Contres', 'Points']
        df = df[colonnes]

        return df
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_salary(player_name):
    try:
        # Trouver l'url de la page du joueur
        name = lookup(player_name, ask_matches = True)
        suffix = get_player_suffix(name)
        url = "https://www.basketball-reference.com"+str(suffix)
        
        # Envoyer une requête à la page sports-reference
        response = requests.get(url)
        response.raise_for_status()  # Vérifiez si la demande a réussi.
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    
    try:
        # Configurer les options pour le navigateur Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Exécuter Chrome en mode sans interface graphique (headless)
        options.add_argument('--disable-gpu')  # Désactiver l'utilisation du GPU pour éviter certains problèmes
        options.add_argument('--no-sandbox')  # Désactiver le mode sandbox pour améliorer la compatibilité
        
        # Initialiser le navigateur Chrome avec les options configurées
        driver = webdriver.Chrome(options=options)
        
        # Charger la page web
        driver.get(url)
        
        # Localiser la table contenant les données souhaitées
        table = driver.find_element(By.ID, 'all_salaries')
        html_content = table.get_attribute('outerHTML') # Extraire le contenu HTML de la table
        
        # Analyser le contenu de la table avec Pandas
        df = pd.read_html(html_content)[0]
        
        # Supprimer les lignes où tous les éléments sont des valeurs manquantes (NaN)
        df = df.dropna(how='all')
        
        # Supprimer le tableau des totals (tableau gris)
        df = df[~df['Season'].str.contains("Career", na=False)]
        
        # Renommer les colonnes
        df.columns = ['Saison', "Équipes", "Ligue", "Salaire"]
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def get_player_logs_clean(nom_joueur):
    # Créer le dataframe des journaux en utilisant l'API 
    df = get_game_logs(nom_joueur, 2024,playoffs=False, ask_matches=True)
    
    # Garder que les colonnes intéressantes
    colonnes = ["DATE","OPPONENT","RESULT","GS","MP","FG","3P","3P%","FT","FT%","AST","PTS"]    
    df = df[colonnes]
    
    # Renommer les colonnes
    df.columns = ["Date", "Adversaire", "Résultat", "Titulaire", "Minutes jouées", 
            "Tirs réussis", "3 points", "3 points %", "Lancers francs", 
            "Lancers francs %", "Passes décisives", "Points"]
    return df

def get_player_splits_clean(nom_joueur):
    # Créer le dataframe des catégories en utilisant l'API
    df = get_player_splits(nom_joueur, 2024)
    # Renommer les colonnes
    df.columns = ["Catégories", "Valeur", "Minutes jouées", "Points", "Rebonds totaux", "Passes décisives"]
    return df

def creation_graphique(df, x, y, dossier):
    # Fonction standard pour créer les graphiques
    fig = plt.figure(figsize=(10, 5))
    plt.bar(df[x], df[y], color='maroon', width=0.4)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"{y} par {x}")
    
    # Sauvegarder le graphique
    plt.savefig(f"{dossier}/Graphique_representant_les_{y}.png", dpi=300, bbox_inches='tight')
    plt.close()
    return

import pandas as pd
import matplotlib.pyplot as plt

def graph_W_L(original_df, dossier):
    # Créer un nouveau DataFrame avec seulement la colonne 'Résultat'
    df = original_df[['Résultat']].copy()
    
    # Extraire la première lettre (W/L) de la colonne 'Résultat'
    df['Résultat_propre'] = df['Résultat'].str[0]
    
    # Assigner les hauteurs des barres : +1 pour les victoires, -1 pour les défaites
    df['Longueur'] = df['Résultat_propre'].apply(lambda x: 1 if x == 'W' else -1)
    
    # Créer une nouvelle colonne pour le numéro du match
    df['Nombre du match'] = range(1, len(df) + 1)
    
    # Créer le graphique à barres
    plt.figure(figsize=(10, 6))
    colors = df['Longueur'].apply(lambda x: 'green' if x > 0 else 'red')  # Vert pour les victoires, rouge pour les défaites
    plt.bar(df['Nombre du match'], df['Longueur'], color=colors)
    plt.xlabel('Nombre du match')
    plt.ylabel('Résultat')
    plt.title('Résultat (Victoires et Défaites)')
    plt.ylim(-1.5, 1.5)  # Définir les limites de l'axe y pour plus de clarté
    
    # Ajouter une ligne horizontale à 0.
    plt.axhline(0, color='black', linewidth=0.8)  # Ligne horizontale à 0
    # Sauvegarde du graphique :
    plt.savefig(f"{dossier}/Résultat_parties.png", dpi=300, bbox_inches='tight')
    plt.close()
    return


def scrapping_joueur(nom_joueur):
    # Création du dossier du joueur
    dossier = creation_dossier(os.path.dirname(__file__), nom_joueur)
    
    # Créer le DataFrame et le sauvegarder dans le fichier
    stats = get_stats(nom_joueur)
    stats.to_csv(f"{dossier}\stats.csv",index =False)
    
    game_highs = get_game_highs(nom_joueur)
    game_highs.to_csv(f"{dossier}\game_highs.csv", index = False)
    
    salary = get_salary(nom_joueur)
    salary.to_csv(f"{dossier}\salary.csv", index = False)
    
    splits = get_player_splits_clean(nom_joueur)
    splits.to_csv(f"{dossier}\splits.csv", index = False)
    
    logs = get_player_logs_clean(nom_joueur)
    logs.to_csv(f"{dossier}\logs.csv",index = False)
    
    # Récupérer l'image du joueur et la sauvegarder.
    image_url = get_player_headshot(nom_joueur)
    img_data = requests.get(image_url).content
    with open(f'{dossier}\{nom_joueur}.jpg', 'wb') as handler:
        handler.write(img_data)
    
    # Création des graphiques
    creation_graphique(stats, "Saison", "Moyenne des Points", dossier)
    creation_graphique(salary, "Saison", "Salaire", dossier)
    graph_W_L(logs,dossier)
    
if __name__ == "__main__":
    menu_joueur()