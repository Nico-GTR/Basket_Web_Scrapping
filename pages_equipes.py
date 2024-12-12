import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Dossiers des données
base_dir = os.getcwd()
equipes_dir = os.path.join(base_dir, "Equipes")
infos_dir = os.path.join(equipes_dir, "Infos_equipe")
logos_dir = os.path.join(equipes_dir, "logo_equipe")
roster_dir = os.path.join(equipes_dir, "Roster")
salaires_dir = os.path.join(equipes_dir, "Salaire")
stats_dir = os.path.join(equipes_dir, "Stats")

# Dossier de sortie pour les fichiers HTML
output_dir = os.path.join(base_dir, "Pages_Equipes")
os.makedirs(output_dir, exist_ok=True)

# Configurer Jinja2
env = Environment(loader=FileSystemLoader(base_dir))
template = env.get_template("equipe_template.html")

# Liste des équipes (basée sur les fichiers fournis)
teams = ["ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

for team in teams:
    try:
        # Charger les fichiers CSV
        infos_file = os.path.join(infos_dir, f"infos_equipe_{team}.csv")
        roster_file = os.path.join(roster_dir, f"roster_{team}.csv")
        salaires_file = os.path.join(salaires_dir, f"salaires_{team}.csv")
        stats_file = os.path.join(stats_dir, f"stats_{team}.csv")

        infos = pd.read_csv(infos_file).iloc[0].to_dict()  # Une seule ligne
        roster = pd.read_csv(roster_file).to_dict(orient="records")
        salaires = pd.read_csv(salaires_file).to_dict(orient="records")
        stats = pd.read_csv(stats_file).to_dict(orient="records")

        # Chemin du logo
        logo_path = os.path.join("Equipes", "logo_equipe", f"{team}.jpg")

        # Remplir le template
        output_from_template = template.render(
            team_name=team,
            logo=logo_path,
            infos_equipe=infos,
            roster=roster,
            salaries=salaires,
            stats=stats
        )

        # Enregistrer le fichier HTML
        output_file = os.path.join(output_dir, f"{team}.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_from_template)
    
    except Exception as e:
        print(f"Erreur lors du traitement de l'équipe {team}: {e}")

print("Fichiers HTML générés avec succès.")