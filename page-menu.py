# -*- coding: utf-8 -*-
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_NAME = 'template.html'

TEAM_LOGOS_FOLDER = 'Equipes/logo_equipe'
PLAYERS_ROOT_FOLDER = 'Joueurs'

# Noms des joueurs
player_names = [
    "Stephen Curry",
    "Lebron James",
    "Derrick Rose",
    "Kevin Durant",
    "Kawhi Leonard",
    "Nikola Jokic",
    "Luka Dončić",
    "Devin Booker",
    "Jayson Tatum",
    "Donnovan Mitchell"
]

# Collecte des données des équipes
teams_data = []
for filename in os.listdir(TEAM_LOGOS_FOLDER):
    if filename.lower().endswith('.jpg'):
        filepath = os.path.join(TEAM_LOGOS_FOLDER, filename)
        logo_title = os.path.splitext(filename)[0]
        teams_data.append({
            "logo": filepath.replace("\\", "/"),  # Corrige les chemins Windows
            "logo_title": logo_title
        })

# Collecte des données des joueurs
players_data = []
for player_name in player_names:
    image_name = player_name + ".jpg"
    image_path = os.path.join(PLAYERS_ROOT_FOLDER, player_name, image_name)
    players_data.append({
        "headshot_url": image_path.replace("\\", "/"),
        "name": player_name
    })

# Configurer Jinja2 pour charger le template HTML
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(TEMPLATE_NAME)

# Remplir le template HTML
output_html = template.render(teams=teams_data, players=players_data)

# Sauvegarder le fichier HTML généré
with open('nba_equipe_joueurs.html', 'w', encoding='utf-8') as f:
    f.write(output_html)

print("Le fichier HTML a été généré avec succès !")
