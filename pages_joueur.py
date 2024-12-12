import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Dossiers des données
base_dir = os.getcwd()
players_dir = os.path.join(base_dir, "Joueurs")
output_dir = os.path.join(base_dir, "Pages_Joueurs")
os.makedirs(output_dir, exist_ok=True)

# Configurer Jinja2
env = Environment(loader=FileSystemLoader(base_dir))
template = env.get_template("joueur_template.html")

# Parcourir les dossiers de joueurs
for player_name in os.listdir(players_dir):
    player_path = os.path.join(players_dir, player_name)
    if os.path.isdir(player_path):
        try:
            # Charger les fichiers spécifiques au joueur
            photo_path = os.path.join(player_path, f"{player_name}.jpg")
            stats_file = os.path.join(player_path, "stats.csv")
            game_highs_file = os.path.join(player_path, "game_highs.csv")
            splits_file = os.path.join(player_path, "splits.csv")
            salary_graph_path = os.path.join(player_path, "salary_chart.jpg")
            results_path = os.path.join(player_path, "results_chart.jpg")

            stats = pd.read_csv(stats_file).to_dict(orient="records")
            game_highs = pd.read_csv(game_highs_file).to_dict(orient="records")
            splits = pd.read_csv(splits_file).to_dict(orient="records")

            # Informations générales du joueur (extraites des stats ou autres)
            infos_joueur = {
                "Nom": player_name,
                "Position": stats[0].get("Position", "N/A"),
                "Équipe": stats[0].get("Team", "N/A")
            }

            # Remplir le template
            output_from_template = template.render(
                player_name=player_name,
                photo=photo_path,
                infos_joueur=infos_joueur,
                stats=stats,
                game_highs=game_highs,
                splits=splits,
                graphique_salaire=salary_graph_path,
                resultats_parties=results_path
            )

            # Enregistrer la page HTML
            output_file = os.path.join(output_dir, f"{player_name}.html")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_from_template)

        except Exception as e:
            print(f"Erreur lors du traitement du joueur {player_name}: {e}")

print("Pages HTML pour les joueurs générées avec succès.")
